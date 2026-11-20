# grep after the distribution

Once normal is known, grep the specific terms:

    grep -i flag access.log
    grep 'admin' access.log

grep -n gives line numbers for context reconstruction.

## Useful greps

- `grep -inE 'flag|ctf'` — the token, case-insensitive + numbered.
- `grep 'Accepted' auth.log` — the successes after failures.
- `grep ' 500 ' access.log` — the error trail.
- `grep -c 'Failed' auth.log` — the failure count for the baseline.
