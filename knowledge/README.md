
Pilot command:

```bash
python3 tools/github_pilot.py --limit 30
```

The pilot pins the repository to a commit, selects Markdown files under web
challenge paths, and delegates fetching to `tools/crawl.py`. It never clones
the complete repository or executes downloaded code.

`python3 tools/queue_extract.py` scores what was fetched and produces the
extraction queue: which pages carry evidence worth turning into a card, in what
order. Nothing in the queue becomes a card without a human reading it first.
