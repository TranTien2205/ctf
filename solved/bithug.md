# BitHug (picoCTF "wily courier") — web

Flag read from a live response. Value not recorded here.

## Shape
Registration silently creates `_/<user>.git` holding the flag. `git-api.ts` allows the
read only for `admin`, and `auth-api.ts` defines admin as **source IP is localhost**.
The repo webhook is the only thing that can originate such a request.

## Three flaws compose
1. The webhook URL is validated when SAVED (`new URL(url)`, port must be `""`/`"80"`,
   host must not be `localhost`/`127.0.0.1`) but `formatString(webhook.url, options)`
   runs when it FIRES. A stored `http://{{ref}}` passes both checks and expands later.
2. `receivePackPost` derives `ref` by raw-parsing the push body
   (`split("\0")[0].split(" ")[2]`) with no validation, so `ref` can be
   `0.0.0.0:1823/_/<user>.git/git-receive-pack`. `0.0.0.0` also sidesteps the
   blocklist, which only string-compares two exact values.
3. `git()` resolves on stdout close regardless of exit code, so git rejecting the
   "funny refname" does not stop the webhooks firing.

## Why not just read the flag over SSRF
The `fetch` response is discarded. Instead use the webhook's attacker-controlled body
and Content-Type to send a full `git-receive-pack` request AS ADMIN, pushing
`refs/meta/config` with `access.conf` = our username; `getAccessConfig()` treats that
as a grant and the repo is then readable normally.

## Traps
- The handout is a plain tar despite the `.tgz` name; `tar tzf` fails and looks like a
  truncated download. Check `file` before blaming the transfer.
- `formatString` also rewrites the BODY, so the packfile must not contain `{{`.
- Build the packfile locally and replay it into a throwaway bare repo with
  `git receive-pack --stateless-rpc` before sending anything to the target.
