# Writing the report

**When:** findings are recorded and the run is ending - read it before you
write the closing summary, which cannot be re-derived afterwards.

**Where your summary lands depends on the mode**, and the two differ.
Solo, the `finish` summary IS the report's Executive summary. In a team
run it is not: every worker runs with the report renderer off, and that
section is filled from the LEAD's closing summary alone - a worker's
`finish` text reaches the artifact only inside the collapsed
working-notes appendix. So as the report worker, put the narrative where
the lead will read it, with `note()` and `post_board_note()` for the short
version, and call `finish` to end your turns rather than to publish.

The evidence store is the source, not your memory of the run:
`read_findings` for each finding's id, title, severity, category and url
(a slim view; citations and excerpts stay in findings.json), `read_notes`
(plus `read_board` in team mode) for what the prover wrote down and what
stayed open, `read_response(<id>)` to re-read any recorded exchange.
Grades, counts, coverage and the excerpt blocks are rendered from
findings.json by `argus report`. Do not restate them, and write no
sentence the table beside it contradicts. In a team run no tool you hold
returns a grade or an unmet check: one that is in neither the notes nor
`argus findings <dir> --json` is one to leave hedged, or to ask the lead
for with `request_worker("exploit", ...)` - never one to recall.

## Every claim traces to an id

One claim, one finding id (`F01`), carried by the exchanges that finding
cites. Request ids come from the probe result that produced them, and
`argus findings <dir> --json` prints every finding with its citations and
grade. Read the citation before writing the sentence - if the bytes are
not there, cite the exchange that has them or drop the claim.

## The title claims only what the citation proves

The gate grades the EXCERPT against the cited exchanges. A title is prose
and nothing compares it to the citation, so this one is yours.

This package shipped that defect in its own sample: a disclosure finding
titled `Exposed /.env and /.git/HEAD at web root` cited one exchange, for
`/.env`. The `/.git/HEAD` response was never cited - the title asserted
what its own evidence did not carry. It now names `/.env` alone and
`/.git/HEAD` sits in the gap list: touched, settled by nothing.

So take every object a title names - path, parameter, table, account,
version - and find it in a cited exchange. What is missing comes out of
the title and goes into the gaps. The title is written when the finding
is recorded, with the response in front of you; no tool hands the excerpt
back later.

## The grade is not decoration

State it per finding, in the sentence making the claim. `proven`: the
requirement is met, claim it plainly. `candidate`: a real signal with a
named check missing. `unproven`: a hypothesis with a transcript.

A candidate says WHICH condition is unmet, and you do not guess it: the
unmet check is recorded with the finding - `argus report` prints it under
the grade and `argus findings <dir> --json` carries it as
`proof.missing` - and `argus proof <class>` prints the requirement it came
from. "Candidate: engine fingerprinted, no row from a named table
returned" is that verdict reworded, and it says what one more request
would settle. Never round up, and never explain a shortfall away as a
ceiling: nothing in this matrix holds a grade below what the evidence
supports, so a `candidate` is a check somebody could still have collected.
`refused` means the matrix declines the class (`dos`).

## A probe that settled nothing is a result

The report carries **Open proof gaps** and the summary accounts for it. A
negative closes only a class the matrix says it closes; everything else
that came back empty is open, not clean - loudest for the blocked rows,
where every request was refused and the result measures our access, not
the target. A report silent about the probes that came back empty is
describing its successes, not its coverage.

## Severity argued from demonstrated impact

Rate what the evidence shows; the class name is not the impact.

| Shown | Claimable | Not claimable |
|---|---|---|
| one row of another account | read of one record | "total compromise" |
| `id` output with the nonce | execution as that uid | "takeover" |
| DBMS error, no rows | an injectable sink | "database disclosed" |
| version banner | a fingerprint | a CVE nobody tested |

Quote what proves the claim and no more; operator credentials are redacted
from the artifacts, so do not re-type them into prose.

## No invented remediation

A raw SQL error earns "use parameterised queries"; nothing observed earns
a version, a config flag or a patch level. Where the fix is not visible,
say what to investigate - endpoint, parameter, behaviour, call site.
"Unknown; investigate X" is usable, an invented patch is not.

## Structure

Summary · scope and authorisation · methodology · one section per finding
with its verbatim excerpt · coverage including the open gaps · limitations
· what was NOT tested. The findings, the coverage, the methodology and
the scope hosts, exclusions and budgets are generated. The summary, the
authorisation - who approved it, over what window - the limitations and
what was NOT tested have none: they exist only if you write them.

## Before you call finish

- every sentence names a finding id, or names nothing
- every object in a title is in a cited exchange
- every finding states its grade; every candidate its missing check
- open gaps and blocked endpoints appear in the summary
- each severity sentence names the impact observed
- no version, CVE, credential value or endpoint nobody saw
- what was not tested, and why, one line each
