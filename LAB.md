# LAB.md — practising on a self-hosted CTF range

This tree is the **brain**: skills, controller, evidence gates. A separate machine
can be the **range**: a host that generates and runs real CTF challenges in
Docker so the agent can solve them and feed the result back into the skill set.

The two sides stay separate on purpose. The range software is licensed
CC-BY-NC-4.0 (non-commercial) and is large; it never enters this repository.

```
Windows host (range)                         Kali VM (brain)
  CTF-Dojo  -> generates challenges            ctf-v2 agent
  docker compose up -> localhost:port   <-->   tools/lab_sync.py
  serve_lab.ps1 -> lab_targets.json            control loop -> hooks.py -> flag
                                               chain card -> field note -> gate
```

## Range side (Windows host)

Scripts live in `lab/windows/`. They are run by the agent or operator on the
Windows host, not from this tree.

| Script | Purpose |
|---|---|
| `lab/windows/install_ctf_lab.ps1` | Install prerequisites and clone CTF-Dojo and Cyber-Zero |
| `lab/windows/start_challenge.ps1` | Start one challenge, find its host port, pack its source, append it to the target list |
| `lab/windows/serve_lab.ps1` | Serve the target list and source archives over HTTP for the VM |

See `lab/windows/README.md` for the exact commands. In short:

```powershell
.\install_ctf_lab.ps1 -Root C:\ctf-lab
cd C:\ctf-lab\CTF-Dojo
.\.venv\Scripts\python.exe ctf_forge.py --filter_category web --max_tasks 5 --workers 4
.\.venv\Scripts\python.exe generate_metadata.py
.\start_challenge.ps1 -ChallengePath C:\ctf-lab\CTF-Dojo\ctf-archive\<event>\<task> -HostIp <windows-lan-ip>
.\serve_lab.ps1 -HostIp <windows-lan-ip>
```

Start with a small batch. The full CTF-Dojo set is hundreds of challenges and its
Docker images can exceed the free disk on a small VM.

## Brain side (Kali VM)

`tools/lab_sync.py` reads the range's target list and prepares local state. It
never probes the target itself.

```bash
python3 tools/lab_sync.py --targets http://<windows-lan-ip>:8899/lab_targets.json --list
python3 tools/lab_sync.py --targets http://<windows-lan-ip>:8899/lab_targets.json \
  --challenge <key> --fetch-source
```

That creates `challenges/<key>/state.json` and, with `--fetch-source`, extracts
the source archive under `challenges/<key>/source/` for white-box classification.
It then prints the bootstrap commands:

```bash
python3 tools/classify.py --source challenges/<key>/source
python3 tools/skill_select.py --source challenges/<key>/source
python3 tools/chain_match.py --source challenges/<key>/source
python3 tools/decide.py <key>
```

From there the normal control loop runs. The proof standard is unchanged: a flag
counts only when it is read from a live response or a supplied artifact and passed
through `tools/hooks.py pre-flag`. The range's `flag_sha256` is a second,
plaintext-free check:

```bash
python3 tools/lab_sync.py --targets <url> --verify <key> '<flag>'
```

## Closing the loop

After a verified flag, follow `LEARNING_LOOP.md`: write the chain card, run
`tools/classify_solve.py --chain <id>`, review the field note, add a golden case,
and run `bash test/run_all.sh`. A challenge solved on the range becomes local
experience only after that loop, never because a writeup or a container said so.

## Rules

- Range targets are local and authorised: the Docker host and its published
  ports. Do not point the agent at anything else.
- Never commit the range repositories, their images, or any flag. Keep the range
  under its own directory on the host.
- Tear a challenge down when finished (`docker compose down -v`) and remove its
  entry from the target list.
- A flag read from a container file is an artifact; a flag read from the live
  response is live-response. Record which one it was.
