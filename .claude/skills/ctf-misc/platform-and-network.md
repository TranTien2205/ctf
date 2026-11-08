# Platform and network surfaces

The scoreboard, the chat server and the resolver are targets in their own
right. Full depth lives in `ctfd-navigation.md` and `dns.md`.

Moved out of `SKILL.md` so the router stays thin. Content is unchanged.

---

## CTFd Platform Navigation (No Browser)

Detect CTFd (`curl -s "$CTF_URL/api/v1/" | head -5`) and interact via API. **Ask the user for their API token** (CTFd Settings > Access Tokens) — it is not provided by default. Then use `Authorization: Token $CTF_TOKEN` header for all requests.

```bash
export CTF_URL="https://ctf.example.com" CTF_TOKEN="ctfd_your_token_here"
curl -s -H "Authorization: Token $CTF_TOKEN" "$CTF_URL/api/v1/challenges" | jq -r '.data[] | "\(.id)\t\(.value)pts\t\(.category)\t\(.name)"'
curl -s -X POST -H "Authorization: Token $CTF_TOKEN" -H "Content-Type: application/json" "$CTF_URL/api/v1/challenges/attempt" -d "{\"challenge_id\": $CID, \"submission\": \"flag{...}\"}"
```

See [ctfd-navigation.md](ctfd-navigation.md) for full workflow, Python client class, session login, hints, notifications, file download, and troubleshooting.

---


## Discord API Enumeration (0xFun 2026)

Flags hidden in Discord metadata (roles, animated emoji, embeds). Invoke `/ctf-osint` for Discord API enumeration technique and code (see social-media.md in ctf-osint).

---


## DNS Exploitation Techniques

See [dns.md](dns.md) for full details (ECS spoofing, NSEC walking, IXFR, rebinding, tunneling).

**Quick reference:**
- **ECS spoofing**: `dig @server flag.example.com TXT +subnet=10.13.37.1/24` - try leet-speak IPs (1337)
- **NSEC walking**: Follow NSEC chain to enumerate DNSSEC zones
- **IXFR**: `dig @server domain IXFR=0` when AXFR is blocked
- **DNS rebinding**: Low-TTL alternating resolution to bypass same-origin
- **DNS tunneling**: Data exfiltrated via subdomain queries or TXT responses


