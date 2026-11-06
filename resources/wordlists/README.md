# resources/wordlists/

Wordlists available to the `wordlist_fuzz` tool. To add one, drop a
`<name>.txt` here — one entry per line, `#` comments allowed — then call
`wordlist_fuzz(base_url=..., wordlist="<name>")`. No code change needed.

- `dirs-small.txt` — small path set for quick discovery
- `params.txt` — common parameter names (use with `mode=param`)
- `api-paths.txt` — API-shaped paths
