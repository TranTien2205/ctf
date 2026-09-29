# Toolchain - what this box actually has

Measured on this machine, not remembered. A runbook line that fails on a missing
parser costs more than the install would have. Re-measure with `command -v` before
trusting any row; this file records a measurement, and a measurement ages.

Measured 2026-09-27 on Python 3.14.6.

## Present, no install needed

| Tool | Version | Artifact family it unlocks |
|---|---|---|
| `tshark` / `capinfos` | 4.0.7 | captures - the whole network family |
| The Sleuth Kit: `fls` `icat` `istat` `mmls` `fsstat` `blkls` `mactime` `tsk_recover` `tsk_gettimes` `img_stat` `ffind` `ifind` | 4.12.0 | disk images, `$MFT`, timelines |
| `sqlite3` | 3.46.1 | browser history, `ActivitiesCache.db`, EDR databases |
| `jq` | 1.8.1 | CloudTrail, any JSON log, EVTX after conversion |
| `7z` / `7za` / `p7zip` | - | bundle intake, **including AES zips that `unzip` cannot read** |
| `bulk_extractor` | 2.1.1 | addresses, URLs and emails out of any blob |
| `binwalk`, `scalpel`, `photorec`, `testdisk` | - | carving and recovery |
| `exiftool` | 13.10 | document and image metadata |
| `qemu-img` | 11.0.3 | virtual disk conversion |
| `pipx` | 1.15.0 | the no-sudo install route |
| python `pandas` | 2.3.3 | **the timeline glue for every family** |
| python `scapy` | 2.6.1 | programmatic capture walks |
| python `pefile` / `olefile` / `capstone` | 2024.8.26 / 0.47 / 5.0.5 | static PE, OLE and disassembly |
| python `numpy` / `matplotlib` / `impacket` | 2.4.6 / 3.10.9 / dev | supporting |

Day-zero capability: the filesystem, network and cloud families are fully workable
with the above. EVTX, registry, prefetch and memory are not.

## Absent, verified

`evtx_dump`, `chainsaw`, `hayabusa`, `zircolite`, `vol` / `volatility3`, `regripper`,
`reglookup`, `hivexsh`, `yara` (CLI), `zeek`, `suricata`, `velociraptor`, `capa`,
`floss`, `plaso` / `log2timeline.py` / `psort.py`, `foremost`, `ewfmount`,
`EvtxECmd`, `MFTECmd`, `RECmd`, `PECmd`, `target-query`.

Python modules absent: `volatility3`, `Evtx`, `regipy`, `dissect`, `pytsk3`,
`pyewf`, `libesedb`, `pyshark`, `construct`, `dpkt`, `oletools`, `polars`.

## Install routes, in order

**Rank 1 - one apt line, unlocks the most.** Simulated before running: 2 upgraded,
23 newly installed, **0 to remove**, roughly 5.9 MB of direct downloads. All
dpkg-managed, so the system Python cannot be broken.

```bash
sudo apt install --no-install-recommends chainsaw python3-evtx libevtx-utils \
  libregf-utils libesedb-utils libscca-utils libolecf-utils libvshadow-utils \
  liblnk-utils libfsntfs-utils oletools ewf-tools yara python3-construct python3-dpkt
```

What each buys:

| Package | Gives | Unlocks |
|---|---|---|
| `chainsaw` | `chainsaw` | Sigma hunting over EVTX. The Kali package **ships its own mappings and an evtx rules tree** under `/usr/share/chainsaw/`, so no separate Sigma clone is needed for a first pass |
| `python3-evtx` | `Evtx` module | scriptable EVTX parsing |
| `libevtx-utils` | `evtxexport` | dependency-free EVTX dump |
| `libregf-utils` | `regfexport`, `regfinfo` | registry hives |
| `libesedb-utils` | `esedbexport` | SRUM, `WebCacheV01.dat`, NTDS |
| `libscca-utils` | `sccainfo` | **prefetch** |
| `liblnk-utils` | `lnkinfo` | LNK and Jump Lists |
| `libfsntfs-utils` | `fsntfsinfo` | NTFS metadata without .NET |
| `libolecf-utils` | `olecfinfo` | OLE compound documents |
| `libvshadow-utils` | `vshadowinfo` | Volume Shadow Copies |
| `oletools` | `olevba` | Office macro extraction |
| `ewf-tools` | `ewfinfo`, `ewfmount` | E01 evidence containers |
| `yara` | `yara` CLI | **replaces the segfaulting Python binding** |

**Rank 2 - `evtx_dump`, no sudo.** A single static binary, the fastest EVTX to JSONL
path, from the `omerbenamram/evtx` GitHub releases. Put it in `~/.local/bin`, which
is already on PATH via pipx. Pass `-t 1` whenever record order matters.

**Rank 3 - memory, no sudo.**

```bash
pipx install volatility3
```

Then the Windows symbol pack, measured at 839,727,133 bytes. Download it before a
memory Sherlock, not during.

**Rank 4 - registry depth.**

```bash
sudo apt install --no-install-recommends regripper reglookup   # simulate first
pipx install regipy
```

Simulate `regripper` first (`apt-get install -s`) and read the removal list: its
Perl dependency closure was not measured here.

**Rank 5 - second-opinion Sigma engines, no sudo.** `hayabusa` and `zircolite` ship
static Linux releases. Both are useful only as a cross-check; chainsaw covers the
first pass. Every public snippet for hayabusa is stale - run `hayabusa --help` and
trust nothing else.

**Rank 6 - added only when a bundle demands it.** `pff-tools` and `python3-pypff`
(PST/OST mail), `libbde-utils` (BitLocker), `libvmdk-utils` / `libqcow-utils`
(virtual disks), `libmsiecf-utils` (IE cache), `zeek` and `suricata` (protocol logs
over a large capture). Every candidate version was verified, but the combined
dependency closure was not, and `zeek` is large.

## Deliberately NOT installed

**`plaso` / `log2timeline`.** An apt simulation showed 4 upgraded, **82 newly
installed, and 1 to remove**: `libafflib0v5`, which is depended on by the installed
`libtsk19` and `sleuthkit`. Installing it swaps The Sleuth Kit from 4.12.0 to 4.14.0
underneath a working toolchain. `mactime` plus pandas covers the same need. If a
bundle genuinely needs a plaso super-timeline, run it in a container.

## Local hazards

- **`python3-yara` segfaults.** Reproduced: `yara.compile()` on a trivial rule exits
  139 (SIGSEGV). `python3-yara 4.5.4-1+b1` against `libyara10 4.3.2-1` is an ABI
  mismatch. Use the `yara` CLI.
- **`pip` is EXTERNALLY-MANAGED** on both Python 3.13 and 3.14. A plain
  `pip install` refuses. Use apt, or pipx, or a fresh venv. Do not reach for
  `--break-system-packages`.
- **The venv at `~/venv` is broken.** Its `pyvenv.cfg` declares 3.13.2 and its
  `site-packages` live under `lib/python3.13`, while its `bin/python3` is an
  absolute symlink to `/usr/bin/python3`, which is now 3.14. Recreate it rather
  than repair it.
- **Only .NET runtime 6.0.8 is installed.** The Eric Zimmerman `/net9/` builds -
  `EvtxECmd`, `MFTECmd`, `RECmd`, `PECmd` - cannot run here. Whether the non-net9
  builds run on 6.0.8 was never tested. Treat EZ Tools as unavailable until proven,
  and use the `lib*-utils` parsers above instead.
- **Disk:** 50 GB free of 197 GB at the time of measurement. Ample for the symbol
  pack; re-check before unpacking a large image.

## Rule

Verify a tool with `command -v` or an import before relying on it, and never claim
output from a tool that was not run. Write every command with a relative or
`$`-derived path: this tree must run wherever it is checked out, and a hardcoded
tree root fails the regression gate.
