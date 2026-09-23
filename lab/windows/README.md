# Windows host: the CTF practice range

This directory is the Windows side of the practice loop. It generates CTF
challenges with Amazon Science CTF-Dojo, runs them in Docker, and exposes a small
target list that the Kali VM agent reads.

The repositories are licensed CC-BY-NC-4.0 (non-commercial). Keep everything under
`C:\ctf-lab` and never vendor it into a repository you own or publish.

## What each script does

| Script | Purpose |
|---|---|
| `install_ctf_lab.ps1` | Install Git, Python and Docker Desktop; clone CTF-Dojo and Cyber-Zero; build the Python venv |
| `start_challenge.ps1` | `docker compose up` one challenge, find its host port, pack its source, and append it to `served\lab_targets.json` |
| `serve_lab.ps1` | Serve `served\` over HTTP so the VM can read the target list and source archives |

## 1. Install

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\install_ctf_lab.ps1 -Root C:\ctf-lab
```

Add `-CloneArchive` to also clone the pwn.college template. That clone is large;
do it only when you have the disk.

## 2. Generate a small batch of challenges

CTF-Forge calls an LLM, so it needs an API key. Start small to protect the disk.

```powershell
cd C:\ctf-lab\CTF-Dojo
$env:DEEPSEEK_API_KEY = "<your-key>"
.\.venv\Scripts\python.exe ctf_forge.py --filter_category web --max_tasks 5 --workers 4
.\.venv\Scripts\python.exe generate_metadata.py
```

Each generated task ends up under `C:\ctf-lab\CTF-Dojo\ctf-archive\<event>\<task>\`
with a `challenge.json` and a `docker-compose.yml`.

## 3. Start a challenge and expose it

Find your Windows LAN IP with `ipconfig`, then:

```powershell
.\start_challenge.ps1 -ChallengePath C:\ctf-lab\CTF-Dojo\ctf-archive\<event>\<task> -HostIp <windows-lan-ip>
```

This prints the target URL, the source archive URL and the expected flag SHA-256.

## 4. Serve the target list

```powershell
.\serve_lab.ps1 -HostIp <windows-lan-ip>
```

Leave it running. The VM reads `http://<windows-lan-ip>:8899/lab_targets.json`.

## 5. Solve from the VM

In the Kali VM, inside the ctf-v2 tree:

```bash
python3 tools/lab_sync.py --targets http://<windows-lan-ip>:8899/lab_targets.json --list
python3 tools/lab_sync.py --targets http://<windows-lan-ip>:8899/lab_targets.json --challenge <key> --fetch-source
```

`lab_sync.py` creates the challenge state and prints the bootstrap commands. From
there the normal control loop runs: classify, dispatch, chain match, decide,
probe, verify the flag through `tools/hooks.py`.

## 6. Stop a challenge

```powershell
cd C:\ctf-lab\CTF-Dojo\ctf-archive\<event>\<task>
docker compose down -v
```

Remove its entry from `C:\ctf-lab\served\lab_targets.json` if you are done with it.

## Notes

- Docker Desktop must be running before `start_challenge.ps1`.
- If the VM cannot reach the host, check the network mode of the VM (NAT versus
  bridged) and the firewall rules the scripts create.
- The flag is verified from the live response on the VM side. The SHA-256 in the
  target list is a second, plaintext-free check.
