# OpSec & Blast Radius — shared-instance discipline

## The rule — a deserialization exploit can brick the box

A gadget that runs `Runtime.exec`/`system`/`Process.Start` is real code on
a shared target. The wrong payload on a challenge-box-with-other-teams is a
destructive write, not a solve. The rules below exist because a "harmless"
RCE gadget is the most dangerous primitive this class carries.

## The safe-payload ladder — escalate in order

```
1. marker     → PWNED_X1 / URLDNS — nothing runs, only detection
2. benign     → id / whoami / nslookup — proves RCE, no side-effect
3. file-read  → cat /flag / open('/flag') — reads, never writes
4. OOB        → curl the flag to your listener — read-only on the target
5. webshell   → a file write — ONLY when 1-4 can't reach the flag
6. destructive → NEVER on a shared instance — never rm/dd/kill/iptables
```

## The specific no-gos on a shared target

| Payload | Why not |
|---|---|
| `rm -rf`, `dd`, `mkfs`, `shred` | destroys the challenge for every team |
| `iptables`/`ip route`/`pkill` | breaks the box's networking/processes |
| `chmod -R`/`chown -R`/`usermod` | permission churn — breaks other teams' access |
| `> /etc/passwd`, `> config` | overwrites auth/config — bricks the app |
| webshell + `?c=` exposed | a URL any team can drive — your access, their RCE |
| `kill -9`/`reboot`/`shutdown` | availability loss = your score + others' |
| fork-bomb/CPU-burner | a `while(1)` gadget — DoS |

## The "only if needed" — file-write as last resort

A webshell is *shared access* — anyone who guesses the path drives it. If
the flag can be read in-band/OOB, prefer that. If a file-write is needed:

- write to a NON-webroot path (`/tmp/<rand>`) you read once then delete
- name it unguessably (`<32-hex>.php`) — `/shell.php` is everyone's
- remove it after — `unlink` via the same chain

## The race — when a gadget is timing-sensitive

A stored-object second-order gadget may fire on EVERY read — a cache-get
that unserializes your object each request. A destructive gadget there
re-fires per read → loops the damage. Prefer a benign/marker gadget for
second-order, or a self-disabling one (the gadget overwrites itself).

## The "your own team only" — the label

On attack-defense (different mode — see `tools/ad/`), a payload that's
*your* team's access is acceptable; on a shared jeopardy instance, the
webshell is everyone's. Tag any persistent-access gadget with the team key
and keep the path unguessable.

## The verification-before-leaving rule

Before closing a challenge:

```
□ is a webshell/persistent file left?  → remove it
□ is a background job/listener still running?  → kill it
□ did a stored-object payload get planted in a shared cache/session/db?
   → overwrite it with the original/empty value
□ is a connection/tunnel open?           → close it
```

## The evidence-vs-side-effect rule

A marker/URLDNS/OOB gadget gives you the SAME confirmation a shell does —
with zero side-effects. The class's proof standard is a *response or OOB
line*, not a shell. Shell access is for when the flag literally can't be
read another way — most CTF flags can.

## The "check the blast_radius note"

Each `knowledge/chains/<id>.md` card carries a `blast_radius` field — read
it before running the card's probe on a shared instance. A card marked
destructive is a recipe that already broke something once.

## Output to record

- Which side-effects the payload caused (file written, cache value, etc.)
- How they were cleaned up, or a note that none were made
