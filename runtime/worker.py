#!/usr/bin/env python3
from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path


def run_worker(
    workspace: str | Path,
    prompt: str,
    command: str | None = None,
    timeout: int = 3600,
) -> dict:
    root = Path(workspace).expanduser().resolve()
    configured = command or os.environ.get("MAU_WORKER_COMMAND")
    if configured:
        argv = shlex.split(configured)
        source = "configured"
        output_file = None
    else:
        if not shutil.which("codex"):
            return {
                "status": "UNAVAILABLE",
                "source": "codex",
                "reason": "Codex CLI is unavailable and MAU_WORKER_COMMAND is not configured",
            }
        handle = tempfile.NamedTemporaryFile(prefix="mau-codex-", suffix=".txt", delete=False)
        output_file = Path(handle.name)
        handle.close()
        argv = ["codex", "exec", "--ephemeral", "--output-last-message", str(output_file), "-"]
        source = "codex"

    executable = argv[0] if argv else ""
    if not executable or ("/" not in executable and not shutil.which(executable)):
        return {"status": "UNAVAILABLE", "source": source, "reason": f"worker executable not found: {executable}"}

    try:
        completed = subprocess.run(
            argv,
            cwd=root,
            input=prompt,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "FAIL",
            "source": source,
            "exit_code": 124,
            "stdout": (exc.stdout or "")[-12000:] if isinstance(exc.stdout, str) else "",
            "stderr": "worker timed out",
        }

    final_message = ""
    if output_file is not None:
        try:
            final_message = output_file.read_text(encoding="utf-8")[-12000:]
        except OSError:
            pass
        try:
            output_file.unlink()
        except OSError:
            pass

    return {
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "source": source,
        "exit_code": completed.returncode,
        "stdout": completed.stdout[-12000:],
        "stderr": completed.stderr[-12000:],
        "final_message": final_message,
    }
