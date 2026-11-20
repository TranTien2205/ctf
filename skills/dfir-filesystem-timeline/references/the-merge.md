# timeline_merge — the merged view

    python3 tools/forensics/timeline_merge.py       --source fs.csv:Date:fs --source usn.csv:TimeStamp:usn       --filetime --challenge <c> --gap 600 --contains '<name>'

`--filetime` attaches to the `--source` it follows; `--answer` emits
the hooks.py pre-flag argv only when `--contains` matched.
