"""Shared bits for the SWE-bench Verified track."""

# Same env for both agents inside the instance container (mini's swebench.yaml values,
# plus PATH so the testbed conda env is first for non-bash tool runners too).
CONTAINER_ENV = {
    "PAGER": "cat", "MANPAGER": "cat", "LESS": "-R", "PIP_PROGRESS_BAR": "off", "TQDM_DISABLE": "1",
    "BASH_ENV": "/root/.bashrc",
    "PATH": "/opt/miniconda3/envs/testbed/bin:/opt/miniconda3/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
}

# One patch-extraction rule for both agents: every change to tracked files, plus new
# untracked files inside sub-directories that don't look like tests or scratch scripts.
# (SWE-bench's harness re-applies the official test files afterwards anyway.)
EXTRACT_PATCH = r"""cd /testbed && git config --global --add safe.directory /testbed >/dev/null 2>&1
git ls-files --others --exclude-standard | grep '/' \
  | grep -viE '(^|/)(tests?|testing)/|(^|/)test_[^/]*$|_test\.py$|repro|debug|scratch|(^|/)patch\.txt$' \
  | while IFS= read -r f; do git add -N -- "$f"; done
git -c core.fileMode=false diff HEAD --no-color --no-ext-diff
"""
