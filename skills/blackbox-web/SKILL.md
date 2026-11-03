---
name: blackbox-web
description: Run a black-box web engagement end to end with argus — scope, recon, classify, probe, prove, report. Use this when handed a URL or a host and asked to find and demonstrate vulnerabilities, when starting a new engagement, or when resuming one that already has a ledger.
---

# Black-box web engagement

The order below is not a preference. Each step exists because skipping it
produces a specific, repeatable failure, and the failure is named.

## 0. Scope and authorisation, before any command

```bash
argus open acme-dmz --objective "web foothold on the DMZ portal" \
  --in-scope 172.31.66.0/24 --out-of-scope 172.31.66.1 \
  --ports 80 443 8080 --tiers passive active intrusive \
  --authorisation "signed SoW 2026-11-01, window 09:00-18:00 ICT, contact: ops@acme"
argus target acme-dmz http://172.31.66.10/
```

An empty scope allows nothing, and the intrusive tier refuses to open without an
authorisation note. **Skipping this step is the one failure that is not
recoverable afterwards** — a command against a host nobody authorised is not
undone by deciding later that it was in scope.

## 1. Breadth first, and it costs no tokens

```bash
argus next acme-dmz          # the controller will say: recon, host-liveness
```

Then walk the ladder: `recon.ports`, `recon.fingerprint`, `fuzz.content`,
`recon.params`, `recon.js_mine`, `scan.nuclei`. All deterministic. Do not open a
hypothesis yet.

Why this order matters: a hypothesis opened before the surface is mapped anchors
everything after it. You will spend the engagement proving or disproving the
first thing you happened to see, and the input that actually mattered was on a
path the front page never linked.

**`recon.js_mine` is the step most often skipped and most often decisive.** The
bundle names endpoints the HTML does not, parameters the forms do not, and
occasionally a credential shape. A 403 is surface too: it says the path exists
and something guards it.

## 2. Classify: one class, one falsifier, per input

For each input worth testing, open **one** hypothesis:

```
ledger.open_hypothesis target=http://... vuln_class=sqli
  statement="the id parameter of /item is concatenated into a SQL query"
  falsifier="a single quote changes neither status, length nor error text"
  entry_point={"param":"id","location":"query"}
```

A hypothesis without a falsifier is a hope. Write the falsifier first: it is the
only thing that will later let you close the branch honestly instead of leaving
it open forever.

Park the inputs you are not going to test, **by name**. An unexamined input that
was never written down becomes, in the report, an input that was tested.

## 3. Probe: the cheapest discriminating step, then the control

`knowledge.playbook vuln_class=<class>` gives the ladder. Two rules:

- **The differential is the measurement, not the payload.** Use
  `http.differential` with `repeat=2`. If the page differs from itself, no single
  difference means anything, and the tool says so.
- **Take the positive control.** One request. A value that certainly exists, a
  path that certainly does not, an account that is certainly entitled. The
  control is the difference between a primitive and a fiction, and it is the
  single most common thing missing from an automated tester's evidence.

## 4. Prove: read the requirement before you probe the class

```bash
argus proof sqli        # or: proof.requirement vuln_class=sqli
```

The requirement tells you what to collect, so you collect it on the first pass
rather than returning to the target after the report has been drafted. Code
execution is `id; echo <nonce>` and nothing else. SQL injection is the DBMS
fingerprint plus one named table and at least one row — five rows is a proof, a
full dump is an incident.

`proof.verify` grades what you already have. Call it *before* `record_finding`:
the gap it names is usually one request away while the target is still in front
of you.

## 5. When a class dies, change the question

The ledger refuses a seventh probe on one class. That refusal is the system
working. The next move is not another payload; it is one of:

- an input kind the first pass skipped — a header, a cookie, a path segment, a
  filename, a websocket frame
- the write path: an input that fails every probe is not closed until you have
  read **who fills the store it is looked up in**
- a different class on the same input
- `knowledge.chain_match` for the stack this target runs

## 6. Report: three sections that never merge

`argus report acme-dmz --write`. Confirmed findings with their checks.
Candidates with the exact missing check. What was never tested, said plainly. An
honest "not demonstrated" survives review; a confident claim that does not is
worth less than nothing, because it costs the reader trust in the rest.

## The failure modes this skill exists to prevent

| Symptom | What actually happened |
|---|---|
| a long session, no findings, many payloads | a hypothesis was never falsified, so the same idea was re-probed in costume |
| a confident finding a reviewer rejects | an asymmetry with no control |
| "the application is vulnerable to XSS" | reflection was read as execution |
| a finding that cannot be reproduced | the proof was a tool's label, not an observation |
| the report lists ten CVEs | version banners were read as exploitability |
