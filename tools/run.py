#!/usr/bin/env python3
"""Record one explicitly supplied command; not a sandbox or autonomous runner."""
import argparse
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid

try:
    from .state import ROOT, atomic_json, path_for
except ImportError:
    from state import ROOT, atomic_json, path_for


def record(name, argv, cwd, timeout):
    if not argv or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("command and positive finite timeout are required")
    cwd = Path(cwd).resolve()
    if not cwd.is_dir() or not cwd.is_relative_to(Path(ROOT).resolve()):
        raise ValueError("cwd must be an existing directory inside the toolkit")
    challenge = Path(path_for(name)).parent
    runs = challenge / "runs"
    if runs.is_symlink():
        raise ValueError("runs directory must not be a symlink")
    directory = runs / uuid.uuid4().hex
    directory.mkdir(parents=True)
    result = {"argv": argv, "cwd": str(cwd), "timeout_seconds": timeout,
              "started_at": time.time(), "status": "running", "returncode": None,
              "artifacts": {"stdout": "stdout.bin", "stderr": "stderr.bin"}}
    metadata = str(directory / "run.json")
    atomic_json(metadata, result)
    started = time.monotonic()
    try:
        with (directory / "stdout.bin").open("wb") as stdout, (directory / "stderr.bin").open("wb") as stderr:
            process = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL,
                                       stdout=stdout, stderr=stderr, shell=False, start_new_session=True)
            try:
                process.wait(timeout=timeout)
                result["status"] = "completed"
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                result["status"] = "timeout"
            result["returncode"] = process.returncode
    except OSError as exc:
        result.update(status="error", error=str(exc))
    finally:
        result["elapsed_seconds"] = time.monotonic() - started
        result["finished_at"] = time.time()
        atomic_json(metadata, result)
    return metadata, result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("name")
    ap.add_argument("--cwd", default=ROOT)
    ap.add_argument("--timeout", type=float, default=30)
    ap.add_argument("command", nargs=argparse.REMAINDER, help="use -- before executable and arguments; options go before name")
    args = ap.parse_args()
    argv = args.command[1:] if args.command[:1] == ["--"] else args.command
    try:
        metadata, result = record(args.name, argv, args.cwd, args.timeout)
    except (OSError, ValueError) as exc:
        ap.error(str(exc))
    print(metadata)
    return 124 if result["status"] == "timeout" else 1 if result["status"] == "error" else result["returncode"] if result["returncode"] >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
