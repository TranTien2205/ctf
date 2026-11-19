# Multi-step chains — the real exploit shapes, staged

## The canonical chain: stored XSS -> bot cookie -> flag

```
1. store a payload the admin page renders           ../web-xss/
2. reproduce the bot locally -> confirm it fires    here
3. payload exfils the bot's flag cookie -> listener  here
4. the flag is the cookie's value -> pre-flag        gate
```

The browser work is steps 2-3 — the reproduction and the exfil. The
payload itself is `../web-xss/`; this skill is the harness that makes
the exfil reliable.

## The apexsurvive chain: XSS -> credential -> RCE

```
1. stored XSS payload developed against local bot   here + xss
2. payload fires in the real bot -> exfil token/cred here
3. replay the credential -> reach a template write   (the chain's next class)
4. template overwrite -> RCE -> flag                 ../web-ssti/ or ../web-command-injection/
```

The local bot confirmed *each stage* before the live fire — the skill
is the development harness for a multi-class chain, not just the
single-payload case.

## The exposed-endpoint chain: session -> file -> flag

```
1. POST /session -> sessionId                        here
2. file:///proc/self/environ -> source -> FLAG env   here
3. or file:///flag -> source -> flag                 here
4. -> pre-flag                                       gate
```

The two-read version: `environ` for the flag-in-env case, the direct
`/flag` for the flag-file case. The environ read often names the flag
path when the direct guess misses.

## The loopback chain: session -> localhost -> admin -> flag

```
1. POST /session -> sessionId                        here
2. localhost/admin -> source -> an admin action      here
3. execute fetch(localhost/admin/flag) -> flag       here
4. -> pre-flag                                       gate
```

The browser's loopback position reaches routes the external view
cannot — the chain is session -> internal route -> flag.

## The egress-blocked chain: XSS -> same-origin write -> read back

```
1. stored payload -> bot's browser                   here + xss
2. payload writes flag to a same-origin store        here
   (profile field, a note, a comment — the app's own origin)
3. you read the store -> flag                        here (or a normal request)
4. -> pre-flag                                       gate
```

When the bot cannot exfil off-origin, the flag never leaves — the
payload stashes it on the app's own origin where you read it back.
The "exfil" is a same-origin write.

## The chain-design principle

Each stage is a different class's primitive — the browser harness is
the *connector*, not the whole chain. The skill owns the drive-a-real-
browser stages (reproduce, fire, exfil, read); the payload class and
the follow-on class own their stages. Design the chain so each stage
is confirmed locally before the live fire — a chain is only as
confirmed as its weakest unverified stage.
