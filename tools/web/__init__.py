"""Reusable web-exploitation speed primitives.

Every module here is importable AND runnable as a CLI in the argparse +
JSON-to-stdout style of tools/chain_match.py. Each one exists because it was
hand-written under contest time pressure at least once:

  pdf_text        extract text from a PDF a target returned
  sanitizer_fuzz  differential grammar sweep against a sanitizer or two parsers
  read_loop       drive a proven arbitrary-file-read over a high-value wordlist
  id_sweep        identifier-existence oracle and IDOR sweep, incl. bulk mode
  http_probe      record a request/response pair in tools/hooks.py post-probe shape

Optional dependencies (mutool, pypdf, requests, httpx) are guarded; a missing
one degrades to a stdlib path and is reported in the JSON, never raised.
"""
__all__ = ["pdf_text", "sanitizer_fuzz", "read_loop", "id_sweep", "http_probe", "httpkit"]
