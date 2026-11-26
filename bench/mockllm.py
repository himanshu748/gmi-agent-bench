"""Scripted OpenAI-compatible server for dry runs (no GMI key needed).

It drives the REAL mini-swe-agent and REAL droid binaries end to end:
  turn 1 -> one shell tool call that writes the reference solution (behavior=solve)
            or a harmless `ls` (behavior=noop)
  turn 2 -> finish (mini: `echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`; droid: plain text)
It recognises mini's `bash` tool and droid's `Execute` tool from the request.
"""
from __future__ import annotations

import base64
import http.server
import json
import threading
from pathlib import Path


def solution_command(solution_dir: Path) -> str:
    files = {str(p.relative_to(solution_dir)): base64.b64encode(p.read_bytes()).decode()
             for p in sorted(solution_dir.rglob("*")) if p.is_file()}
    payload = json.dumps(files)
    return ("python3 -c \"import base64,json,pathlib,sys;"
            "[pathlib.Path(k).write_bytes(base64.b64decode(v)) for k,v in json.loads(sys.argv[1]).items()]\" "
            f"'{payload}'")


class MockLLM:
    def __init__(self, solution_dir: Path | None, behavior: str = "solve"):
        self.command = solution_command(solution_dir) if (behavior == "solve" and solution_dir) else "ls -la"
        self._server = None

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self._server.server_address[1]}/v1"

    def _reply(self, req: dict) -> dict:
        tools = {t.get("function", {}).get("name") for t in req.get("tools") or []}
        msgs = req.get("messages") or []
        n_tool_results = sum(1 for m in msgs if m.get("role") == "tool")
        def call(name, args):
            return {"role": "assistant", "content": "Applying fix.", "tool_calls": [
                {"id": f"call_{n_tool_results}", "type": "function",
                 "function": {"name": name, "arguments": json.dumps(args)}}]}, "tool_calls"
        if "bash" in tools:  # mini-swe-agent
            if n_tool_results == 0:
                return call("bash", {"command": self.command})
            return call("bash", {"command": "echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"})
        if "Execute" in tools and n_tool_results == 0:  # droid
            return call("Execute", {"summary": "Apply the reference fix now", "command": self.command,
                                    "riskLevel": "medium"})
        return {"role": "assistant", "content": "Done."}, "stop"

    def start(self) -> "MockLLM":
        mock = self

        class H(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, *a):
                pass

            def do_GET(self):
                self._send({"data": [{"id": "mock"}]})

            def _send(self, obj):
                d = json.dumps(obj).encode()
                self.send_response(200)
                self.send_header("content-type", "application/json")
                self.send_header("content-length", str(len(d)))
                self.end_headers()
                self.wfile.write(d)

            def do_POST(self):
                req = json.loads(self.rfile.read(int(self.headers.get("content-length") or 0)) or b"{}")
                msg, finish = mock._reply(req)
                usage = {"prompt_tokens": len(json.dumps(req)) // 4, "completion_tokens": 40,
                         "total_tokens": len(json.dumps(req)) // 4 + 40,
                         "prompt_tokens_details": {"cached_tokens": 0}}
                model = req.get("model", "mock")
                if req.get("stream"):
                    self.send_response(200)
                    self.send_header("content-type", "text/event-stream")
                    self.end_headers()
                    delta = dict(msg)
                    if "tool_calls" in delta:
                        delta["tool_calls"] = [dict(tc, index=i) for i, tc in enumerate(delta["tool_calls"])]
                    for chunk in (
                        {"choices": [{"index": 0, "delta": delta, "finish_reason": None}]},
                        {"choices": [{"index": 0, "delta": {}, "finish_reason": finish}]},
                        {"choices": [], "usage": usage},
                    ):
                        chunk.update(id="mock", object="chat.completion.chunk", created=0, model=model)
                        self.wfile.write(b"data: " + json.dumps(chunk).encode() + b"\n\n")
                    self.wfile.write(b"data: [DONE]\n\n")
                else:
                    self._send({"id": "mock", "object": "chat.completion", "created": 0, "model": model,
                                "choices": [{"index": 0, "message": msg, "finish_reason": finish}], "usage": usage})

        self._server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        self._server.daemon_threads = True
        threading.Thread(target=self._server.serve_forever, daemon=True).start()
        return self

    def stop(self):
        if self._server:
            self._server.shutdown()
            self._server.server_close()
