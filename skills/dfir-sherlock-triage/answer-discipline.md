# Answer discipline

A correct finding submitted in the wrong shape is graded wrong and costs an
attempt. This file is read before the first answer is submitted, not after the
first one is rejected.

## What the grader actually receives

Read from HTB's own authoring template, fetched from
`hackthebox/public-templates`, file `Sherlock/Sherlock-Questions-Template.yaml`
(145 lines, 20 question slots). Each slot is exactly:

```yaml
- number: 1
  type: free
  title: question text
  flag: answer
  answer_case_sensitive: false
  placeholder: formatting stuff in answer box
  requires: null
```

Five consequences, each traceable to a field above:

1. **`flag` is HTB's internal name for the ANSWER.** A Sherlock answer is not
   flag-shaped and no `flag{...}` regex applies to it. This tree's
   `tools/hooks.py pre-flag` accepts `--source artifact` and applies no format
   regex, so a timestamp, a bare username or a full command line records cleanly.
2. **`answer_case_sensitive: false` is the template default.** Case is normally
   forgiving. Do not rely on it for a question that overrides it.
3. **`placeholder` is rendered inside the answer box.** It is where a format hint
   lives - and it is routinely invisible in a writeup, so a transcribed question
   is not the whole question.
4. **The format hint is ALSO written into `title`.** HTB Nuts task 4 reads
   "Provide the timestamp in UTC format (YYYY-MM-DD HH:MM)" - minute precision,
   no seconds, stated in the question text itself. Read both fields, every time.
5. **`requires` semantics are UNVERIFIED.** The template only ever shows
   `requires: null`, and neither HTB help article states what it does. Do not
   claim it implements a linear/locked mode.

## Answer value types actually observed

Verbatim from the eight answers of one Sherlock (Brutus), which is the widest
single sample where every answer was read rather than inferred:

| Shape | Example |
|---|---|
| IPv4 address, bare | `65.2.161.68` |
| Username, bare, no domain | `root` |
| Timestamp, space separator, seconds | `2024-03-06 06:32:45` |
| Integer identifier | `37` |
| ATT&CK sub-technique id | `T1136.001` |
| Integer seconds (a duration) | `279` |
| Full command line | the command as logged, verbatim |

Other in-question directives seen verbatim across sampled Sherlocks:
`(provide the full command)`, `(technique name)`, `Provide the SHA1 hash of this
file`, `Provide the name of the process`.

## The timezone trap, which is the one that actually costs answers

Timestamps are UTC by convention, and precision varies per question. Three tools
in this directory's runbooks silently render the wrong thing by default:

| Tool | Default | What to pass |
|---|---|---|
| `chainsaw` | UTC | nothing; `--local` would BREAK it |
| `hayabusa` | LOCAL time | `-U` / `--UTC`, and the long ISO flag is lowercase `--iso-8601` |
| `evtx_dump` | multithreaded, records OUT OF ORDER | `-t 1` whenever order matters |

The `evtx_dump` one is the subtle failure: output is complete and correct but not
chronological, so any "what happened first" answer read off the top of the file is
wrong without a warning. Sort explicitly, or pass `-t 1`.

Normalise every timeline to UTC before merging. In pandas:

```python
pandas.to_datetime(series, utc=True)   # a mixed-offset column degrades to
                                       # object dtype and sorts wrongly without this
```

## Precision rules

- Match the precision the question asks for. `YYYY-MM-DD HH:MM` means minutes; do
  not append seconds, and do not round a 06:32:45 up to 06:33.
- A duration answer is two artifact timestamps subtracted, not an estimate.
- A hash answer is the algorithm the question names. Amcache stores SHA-1; a
  question asking for SHA-256 needs the sample itself, not the Amcache value.
- A path answer is quoted as the artifact writes it, including drive letter and
  case. A KAPE-shaped bundle may store it URL-encoded as `C%3A` - decode before
  answering, and say which form the artifact held.

## Recording an answer in this tree

```bash
python3 tools/hooks.py pre-flag <sherlock>-qN --value '<answer>' \
  --source artifact --evidence '<verbatim excerpt of the record that proves it>'
python3 tools/decide.py <sherlock>-qN
```

`--evidence` is the artifact line itself, not a description of it. An answer whose
evidence is a summary, a tool's verdict, or a writeup's claim has not been proven
and does not enter state.

## Before submitting

1. Both `title` and `placeholder` read, for this question specifically.
2. The value copied from a verbatim artifact excerpt, not retyped from memory.
3. Timezone confirmed UTC, precision matched to the request.
4. The artifact and the exact record identified, so a wrong grade can be diagnosed
   against evidence rather than re-guessed.
