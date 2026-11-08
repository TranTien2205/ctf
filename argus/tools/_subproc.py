"""Bounded subprocess capture: stdout/stderr land in temp files, not memory.

A runaway scanner or exploit PoC printing gigabytes used to exhaust memory
via subprocess.run(capture_output=True) before the result string was ever
sliced. Redirecting to temp files bounds memory by disk instead - we read
back only the head (transcript) and tail (model view) we actually keep.
"""
from __future__ import annotations

import re
import subprocess
import tempfile


def run_capped(cmd: list[str], timeout_s: float, cwd: str | None = None,
               env: dict | None = None,
               needle: str | None = None) -> tuple[int, str, str, bool]:
    """Run cmd; return (returncode, head_text, tail_text, needle_found).

    head_text: first bytes of stdout + first bytes of stderr (audit view).
    tail_text: last bytes of each stream (model view - scanner summaries
    and proof markers live at the end).
    needle: optional regex - searched across BOTH full streams so a proof
    marker in the middle of a huge output is still caught."""
    with tempfile.TemporaryFile(mode="w+b") as fo, \
            tempfile.TemporaryFile(mode="w+b") as fe:
        proc = subprocess.run(cmd, stdout=fo, stderr=fe,
                              timeout=timeout_s, cwd=cwd, env=env)
        so_size, se_size = fo.tell(), fe.tell()

        def _rd(tf, off: int, n: int) -> str:
            tf.seek(off)
            return tf.read(n).decode("utf-8", "replace")

        head = _rd(fo, 0, 45_000)
        shead = _rd(fe, 0, 5_000)
        tail = _rd(fo, max(0, so_size - 15_000), 15_000)
        stail = _rd(fe, max(0, se_size - 5_000), 5_000)
        found = False
        if needle:
            rx = re.compile(needle.encode())
            for tf in (fo, fe):
                tf.seek(0)
                overlap = b""
                while chunk := tf.read(65536):
                    window = overlap + chunk
                    if rx.search(window):
                        found = True
                        break
                    # markers are short; a 4K carry-over catches matches
                    # straddling the read boundary
                    overlap = window[-4096:]
                if found:
                    break
    head_full = head + ("\n[stderr]\n" + shead if shead else "")
    tail_full = tail + ("\n[stderr]\n" + stail if stail else "")
    return proc.returncode, head_full, tail_full, found
