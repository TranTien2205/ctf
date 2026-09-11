# Regression Tests

Run from any directory with:

```bash
python3 ~/ctf/test/regression.py
python3 -m unittest discover -s ~/ctf/tests -v
python3 ~/ctf/selfcheck.py
```

These tests are offline and do not execute challenge artifacts or contact live
targets. They verify routing, skill-path integrity, source scanning, related
card retrieval, state priority preservation, evidence policy, and the known
Weather App source chain. They are a guardrail for updates, not a solving
benchmark.
