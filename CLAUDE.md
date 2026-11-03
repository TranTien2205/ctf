# Operating rules for this repository

argus is an evidence-gated penetration-testing agent system. Read `README.md`
for what it is and `ARCHITECTURE.md` for how the four planes fit together. This
file is the short version of what to do and not do while working in here.

## When you are using the system

1. **Start with the ledger, not with a probe.** `argus next <engagement>` (or
   `ledger.next_action`) is computed from recorded evidence, so it does not drift
   with the conversation. Depart from it when you have a reason, and say the
   reason in one line.
2. **Read the proof requirement before probing a class.** `argus proof <class>`.
   It tells you what to collect, so you collect it on the first pass.
3. **Every probe names a hypothesis.** A probe that names none cannot falsify
   anything, and the broker refuses it.
4. **A refusal is a decision.** `out-of-scope`, `tier-not-enabled`,
   `class-mismatch`, `budget-spent`, `unproven`, `refused-class`. Read the
   message and change the request; never retry the same call verbatim.
5. **Nothing is invented.** No endpoint, parameter, version, CVE, credential or
   number that was not observed here. A scanner label, a template id, a timeout
   and a 500 are candidates.

## When you are changing the system

- `bash test/run_all.sh` before you accept any change. Four layers: unit,
  consistency, harness, end-to-end. `ARGUS_SKIP_E2E=1` is for iterating, never
  for passing.
- **The gate checks that documentation names only things that exist.** If you
  rename a tool or a command, the gate will find every file that still names the
  old one. That is deliberate: a README that names a removed command is a
  correctness bug in a system whose claim is that it does not invent things.
- Adding a class, a ladder, a CVE script, a tool or a model profile is covered by
  `skills/extending-argus/SKILL.md`. Three of the four are data files.
- A new proof class needs a case in `test/cases/proof_cases.json` **in both
  directions**: an evidence set that must grade `proven`, and one that must not.
  The second is the one that matters.
- Keep the package standard-library only. An engagement should not fail on a pip
  install, and the whole thing currently runs on a stock Python 3.14.
- `engagements/` is runtime output. Never commit it, never read another
  engagement's evidence to answer a question about this one.

## What this repository will not help you do

Denial of service, persistence, lateral movement, credential dumping, data
exfiltration, or any demonstration whose proof is the damage. Code execution is
proven with `id; echo <nonce>` and stops there. If a task needs more than that,
it needs a human deciding, not a better prompt.

Authorised testing only. The intrusive tier refuses to open without an
authorisation note naming who authorised it and over what window.
