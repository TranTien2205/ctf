"""Reusable web-exploitation speed primitives.

Every module here is importable AND runnable as a CLI in the argparse +
JSON-to-stdout style of tools/chain_match.py. Each one exists because it was
hand-written under contest time pressure at least once:

  pdf_text        extract text from a PDF a target returned
  sanitizer_fuzz  differential grammar sweep against a sanitizer or two parsers
  read_loop       drive a proven arbitrary-file-read over a high-value wordlist
  id_sweep        identifier-existence oracle and IDOR sweep, incl. bulk mode
  http_probe      record a request/response pair in tools/hooks.py post-probe shape
  variant_matrix  one request per payload SHAPE at one injection point, baseline-diffed
                  and ranked, so twenty hypotheses cost one command instead of twenty
  race_probe      overlapping requests with a serial baseline, because a signature that
                  also appears serially is not a race
  bundle_miner    recover the front-end's real source from a bundle and its source map;
                  a map is attacker-controlled data, so a traversal in `sources` is
                  rejected and counted
  session_dissect name a session token's format before attacking it, and say which
                  standard weakness applies; analysis only, it never forges or sends

Optional dependencies (mutool, pypdf, requests, httpx) are guarded; a missing
one degrades to a stdlib path and is reported in the JSON, never raised.
"""
__all__ = ["pdf_text", "sanitizer_fuzz", "read_loop", "id_sweep", "http_probe", "httpkit",
           "variant_matrix", "race_probe", "bundle_miner", "session_dissect"]
