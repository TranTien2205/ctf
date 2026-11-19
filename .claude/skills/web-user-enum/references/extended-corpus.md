# Extended corpus — the rare and boundary payload set

## The boundary usernames

```
''             a            aa           aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
admin'         "admin"      <admin>      {{admin}}      %admin%
admin|x        admin&x      admin;x      `admin`        $(admin)
{{7*7}}        ${7*7}       <%=7*7%>     {{config}}
admin..        ..admin      .admin       admin.
admin%00       %00admin     admin%ff     admin%0a
admin/../x     ../admin     /admin       admin/
```

Each tests a different code path — an injection-shaped name that returns
a DIFFERENT oracle shape is a different class (`web-sqli`/`web-ssti`/
`web-command-injection`), not this one. Record the boundary case; route
the injection to the neighbor.

## The normalization-boundary set

```
admin     Admin     ADMIN     aDmin     ADMIN@x.c
admin@x.c admin@X.C admin@corp.   admin@corp.com.
'admin ' ' admin'  'admin'  'admin%20' '%20admin'
admin	 admin
admin admin%09 admin%0aadmin admin
```

Case/whitespace/encoding normalization — a `Admin` that hits the same
oracle confirms normalization.

## The unicode/normalization set

```
admin    admin    admin    admin
admin    admin    admin    admin
```

A lookalike (`admin` in Cyrillic ``) that hits a DIFFERENT user than
ASCII `admin` is a homoglyph-confusion — a different finding.

## The multi-valued set

```bash
curl -d 'user=admin&user=zzz&pass=x' "$BASE/login"          # dup param
curl -d 'user[]=admin&pass=x' "$BASE/login"                  # array
curl -H 'Content-Type: application/json' -d '{"username":["admin","zzz"],"password":"x"}' "$BASE/api/login"
curl -d 'user=admin,zzz&pass=x' "$BASE/login"                # comma
```

A `user=admin&user=zzz` that the app reads first-vs-last differently is
a param-pollution — `web-parser-diff`, not this class.

## The type-coercion set

```bash
curl -d 'user=0&pass=x' "$BASE/login"      # numeric 0
curl -d 'user=-1&pass=x' "$BASE/login"     # negative
curl -d 'user[]=x&pass=x' "$BASE/login"    # array in a scalar slot
curl -d 'user={"a":"b"}&pass=x' "$BASE/login"  # object
curl -d 'user=true&pass=x' "$BASE/login"   # boolean
```

A `user[]=x` that crashes or produces a different oracle is a parser-
gap — `web-parser-diff`/`web-nosqli`.

## The traversal/encoding set

```
%61dmin    %2561dmin    %u0061dmin    &#97;dmin    %c0%61dmin
adm%69n    admin%ZZ     admin%E0%80%80n   admin%f0%80%80%8dn
```

Double-encoded/utf8-overlong/entity-encoded `admin` — a decoder that
reads it differently is `web-parser-diff`; a normalization that reads
it the SAME is a normalization note.

## The account-state set

```
locked   disabled   pending   unverified   expired   banned   deleted
```

A `locked`/`pending`/`disabled` user that returns a DIFFERENT message
than a real active user — the state-message oracle.

## The oracle-only set — the three arms, always

Whatever the payload, the measurement is the same three arms:
`KNOWN` vs `FAKE` vs `FAKE2` on the same channel. The payload names the
slot; the channel files carry the measurement.
