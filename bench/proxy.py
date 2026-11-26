"""Metering proxy: sits between an agent and the OpenAI-compatible upstream.

Both agents talk to the same local proxy, which forwards every request to GMI
Cloud (or to the mock server in a dry run) and logs one JSON line per model
call: latency, HTTP status, prompt/completion/cached tokens. This gives one
agent-independent measurement of steps and tokens for both agents, instead
of trusting each tool's own accounting.
"""
from __future__ import annotations

import http.server
import json
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

# Per-socket-read timeout to the upstream. GMI occasionally stalls a request
# indefinitely; failing fast (502) lets the agent's own retry logic take over.
UPSTREAM_TIMEOUT = float(__import__("os").environ.get("BENCH_UPSTREAM_TIMEOUT", "180"))

HOP = {"host", "content-length", "connection", "accept-encoding", "transfer-encoding"}


def _usage_fields(usage: dict | None) -> dict:
    usage = usage or {}
    details = usage.get("prompt_tokens_details") or {}
    cached = details.get("cached_tokens") or usage.get("cache_read_input_tokens") or 0
    return {
        "prompt_tokens": int(usage.get("prompt_tokens") or 0),
        "completion_tokens": int(usage.get("completion_tokens") or 0),
        "cached_tokens": int(cached or 0),
        "usage_reported": bool(usage),
    }


class MeteringProxy:
    def __init__(self, upstream: str, log_path: Path, api_key: str | None = None, guard=None):
        self.guard = guard  # optional: .allowed() -> bool, .add(row) after each call (budget cap)
        self.upstream = upstream.rstrip("/")
        self.log_path = Path(log_path)
        self.api_key = api_key  # injected upstream so agents never need the real key
        self._lock = threading.Lock()
        self._server: http.server.ThreadingHTTPServer | None = None

    @property
    def base_url(self) -> str:
        assert self._server
        return f"http://127.0.0.1:{self._server.server_address[1]}/v1"

    def _record(self, row: dict) -> None:
        with self._lock, self.log_path.open("a") as fh:
            fh.write(json.dumps(row) + "\n")
        if self.guard is not None:
            self.guard.add(row)

    def start(self) -> "MeteringProxy":
        proxy = self

        class Handler(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"  # close-delimited bodies make SSE relay simple

            def log_message(self, *args):
                pass

            def _forward(self, method: str):
                n = int(self.headers.get("content-length") or 0)
                body = self.rfile.read(n) if n else None
                path = self.path[3:] if self.path.startswith("/v1") else self.path
                url = proxy.upstream + path
                headers = {k: v for k, v in self.headers.items() if k.lower() not in HOP}
                # Cloudflare in front of GMI rejects urllib's default UA (HTTP 403 / error 1010).
                if not any(k.lower() == "user-agent" for k in headers):
                    headers["User-Agent"] = "gmi-agent-bench/0.1"
                if proxy.api_key:
                    headers["Authorization"] = f"Bearer {proxy.api_key}"
                req_json = {}
                if body:
                    try:
                        req_json = json.loads(body)
                    except ValueError:
                        pass
                if proxy.guard is not None and path.endswith("/chat/completions") and not proxy.guard.allowed():
                    msg = json.dumps({"error": {"message": "gmi-agent-bench budget cap reached"}}).encode()
                    self.send_response(429)
                    self.send_header("content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(msg)
                    proxy._record({"ts": time.time(), "path": path, "status": 429, "latency_s": 0,
                                   "error": "budget cap", **_usage_fields(None)})
                    return
                t0 = time.time()
                row = {"ts": t0, "path": path, "model": req_json.get("model"),
                       "stream": bool(req_json.get("stream")), "n_messages": len(req_json.get("messages") or [])}
                try:
                    resp = urllib.request.urlopen(
                        urllib.request.Request(url, data=body, headers=headers, method=method), timeout=UPSTREAM_TIMEOUT)
                    status = resp.status
                except urllib.error.HTTPError as e:
                    resp, status = e, e.code
                except Exception as e:  # network error
                    msg = json.dumps({"error": {"message": f"proxy upstream error: {e}"}}).encode()
                    self.send_response(502)
                    self.send_header("content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(msg)
                    row.update(status=502, latency_s=time.time() - t0, error=str(e), **_usage_fields(None))
                    if path.endswith("/chat/completions"):
                        proxy._record(row)
                    return
                ctype = resp.headers.get("content-type", "")
                self.send_response(status)
                for k, v in resp.headers.items():
                    if k.lower() not in HOP:
                        self.send_header(k, v)
                self.end_headers()
                usage, finish, err = None, None, None
                if "text/event-stream" in ctype:
                    for line in resp:
                        self.wfile.write(line)
                        self.wfile.flush()
                        s = line.strip()
                        if s.startswith(b"data:") and s[5:].strip() not in (b"", b"[DONE]"):
                            try:
                                chunk = json.loads(s[5:])
                            except ValueError:
                                continue
                            if chunk.get("usage"):
                                usage = chunk["usage"]
                            for ch in chunk.get("choices") or []:
                                finish = ch.get("finish_reason") or finish
                else:
                    data = resp.read()
                    self.wfile.write(data)
                    try:
                        j = json.loads(data)
                        usage = j.get("usage")
                        if j.get("choices"):
                            finish = j["choices"][0].get("finish_reason")
                        if j.get("error"):
                            err = str(j["error"])[:300]
                    except ValueError:
                        pass
                row.update(status=status, latency_s=round(time.time() - t0, 3), finish_reason=finish,
                           error=err, **_usage_fields(usage))
                if path.endswith("/chat/completions"):
                    proxy._record(row)

            def do_POST(self):
                self._forward("POST")

            def do_GET(self):
                self._forward("GET")

        self._server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._server.daemon_threads = True
        threading.Thread(target=self._server.serve_forever, daemon=True).start()
        return self

    def stop(self) -> None:
        if self._server:
            self._server.shutdown()
            self._server.server_close()


def summarize(log_path: Path) -> dict:
    rows = []
    if Path(log_path).is_file():
        rows = [json.loads(x) for x in Path(log_path).read_text().splitlines() if x.strip()]
    ok = [r for r in rows if r.get("status") == 200]
    return {
        "requests": len(rows),
        "ok_requests": len(ok),
        "failed_requests": len(rows) - len(ok),
        "prompt_tokens": sum(r["prompt_tokens"] for r in rows),
        "cached_tokens": sum(r["cached_tokens"] for r in rows),
        "completion_tokens": sum(r["completion_tokens"] for r in rows),
        "usage_missing": sum(1 for r in ok if not r.get("usage_reported")),
        "model_latency_s": round(sum(r.get("latency_s", 0) for r in rows), 2),
        "first_error": next((f"{r['status']}: {r.get('error')}" for r in rows if r.get("status") != 200), None),
    }
