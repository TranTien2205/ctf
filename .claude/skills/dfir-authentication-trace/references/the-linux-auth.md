# linux_auth.py — auth.log + wtmp together

    linux_auth.py --authlog auth.log --wtmp wtmp --year 2024 \
      --challenge <sherlock>-qN

`--event`/`--user`/`--ip`/`--ut-type`/`--contains` narrow; `--answer`
builds the pre_flag_argv. The year flag pins the syslog year the
lines omit.

## The join

--authlog + --wtmp + --year for the syslog year.

## The year

--year pins the syslog year.
