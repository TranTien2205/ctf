# evtx_query — field joins, honest misses

    evtx_query.py --input security.jsonl --event-id 4624 \
      --field-contains LogonType=10 --challenge <c> --answer IpAddress

`matches` is a list (there is no scalar `matched`); `answer.value`
is the field; `answer.pre_flag_argv` holds the record verbatim —
paste it, never retype.

## The argv

answer.pre_flag_argv carries the record — paste it.

## matches

A list — no scalar matched.
