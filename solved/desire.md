# Desire — HackTheBox, web

`154.57.164.68:30732`. Two services behind one port: a Go/Fiber app on `:1337`
and a Node/Express SSO on `:8080` that the Go app calls over loopback for
`/register` and `/login`. Redis on `:6379`. Handout:
`challenges/Desire/Desire`. Flag: read live from `GET /user/admin`.

## Where the flag is

`ENV FLAG=HTB{REDACTED}` in the Dockerfile — an environment variable, not a
file. The only route to it is `services/http.go:147-162`:

```go
func DesireIsEnigma(c *fiber.Ctx) error {
	userStruct, ok := user.(User)
	...
	if userStruct.Role == "admin" {
		return c.Render("admin", fiber.Map{"FLAG": os.Getenv("FLAG")})
	}
	return utils.ErrorResponse(c, "You are not admin !", http.StatusForbidden)
}
```

So the whole challenge is: make `userStruct.Role == "admin"`.

## The bug

`Role` is not looked up. It is whatever is in a file on disk:

```go
// services/http.go:164-179
func SessionMiddleware(c *fiber.Ctx) error {
	sessionID := c.Cookies("session")
	username := c.Cookies("username")
	if sessionID == "" || username == "" { return c.SendStatus(401) }
	session, err := GetSession(username)          // <- the COOKIE, unvalidated
	...
	c.Locals("user", *session)

// services/sessions.go:37-53
func GetSession(username string) (*User, error) {
	sessionID, err := utils.RedisClient.Get(username)
	sessionJSON, err := os.ReadFile(filepath.Join("/tmp/sessions", username, sessionID))
	var session User
	err = json.Unmarshal(sessionJSON, &session)
	return &session, nil
```

Three things line up:

1. **The `session` cookie is never verified.** The middleware only tests that it
   is non-empty; `session=x` is accepted. The identity is the *other* cookie,
   `username`, in plaintext.
2. **`username` is a path component.** `filepath.Join` normalises dot segments,
   so `username=../../app/service/files/<me>` moves the read from
   `/tmp/sessions` to the archive extraction directory. `http.go:56` rejects
   `/ . \` **at registration**, which makes the account name look safe and hides
   that the same value comes back as an unvalidated cookie. No account with that
   name has to exist.
3. **The session id is predictable, and mintable without a password.**

```go
// services/http.go:73-79  -- note the order
sessionID := fmt.Sprintf("%x", sha256.Sum256([]byte(strconv.FormatInt(time.Now().Unix(), 10))))
err := PrepareSession(sessionID, credentials.Username)   // redis.Set(username, sessionID)
if err != nil { ... }
user, err := loginUser(credentials.Username, credentials.Password)   // ONLY NOW is the password checked
```

`PrepareSession` runs **before** `loginUser`. A `POST /login` carrying the
traversal string as the username and a deliberately wrong password answers
`400 {"error":"Invalid username or Password"}` and has *already* written
`redis[<traversal string>] = sha256(unix_seconds)`.

And the file itself is placed by the upload, which extracts into a directory
named after the *real* logged-in account (`http.go:131-138`), so no traversal
inside the archive is needed at all.

## The chain

```
register + login normally                  -> a real session, and files/<me>/ as the extraction dir
POST /login  username=../../app/service/files/<me>  password=wrong
                                           -> 400, but redis[that string] = sha256(T)
POST /user/upload  (real cookies)          -> a zip whose entry names are sha256 of each
   entry sha256(T-2..T+2) =                   candidate second, covering the clock skew
   {"username":"<me>","id":1,"role":"admin"}
GET /user/admin
   Cookie: session=<real sid>; username=../../app/service/files/<me>
                                           -> 200, admin.html, FLAG
```

`exploits/desire_pwn.py` in the workspace does all four steps; it printed the
flag on the first run.

## What cost time, and the two traps worth keeping

**The archive was the wrong layer, and it argued convincingly for itself.** The
upload extracts with `mholt/archiver v3.5.0`, so Zip Slip was the obvious
hypothesis and it produced a *false confirmation*: `hello.txt` collides with
`file already exists`, `./hello.txt` and `a/../hello.txt` collide, but
`../hello.txt` answers a clean `202`. That asymmetry reads as "the traversal is
not stripped". It is the opposite: `Unarchive` does
`if z.ContinueOnError || IsIllegalPathError(err) { continue }`, so an escaping
entry is **silently skipped** and the handler still answers 202. The control
that broke it: upload the same escaping entry twice. A write that landed must
collide on the second attempt; it never did, and `../../files` — a directory
that certainly exists — also answered 202.

**Because the extractor refuses to overwrite, the error is a file-existence
oracle — but only inside the destination.** Every escaping probe answers 202, so
a sweep for `users.json`, `*.db`, `views/`, the binary, all read as "nothing is
there" regardless of what is actually there. Fourteen probes wasted on a sweep
whose negatives meant nothing. Run a control on a path you know exists *before*
trusting an oracle.

**A bare `Internal Server Error` and a JSON error mean different things.** Fiber's
default 500 is the redis lookup missing; the handler's own failures are JSON.
The bare one is itself the proof that the cookie is the redis key.

## The measurement that was right, and the inference that was one step short

A parallel `ctf-web-files` agent found a genuinely separate bug in the same
extractor, which the source read confirms: `Zip.CheckPath` is a **string** prefix
test, not a path boundary —

```go
to, _ = filepath.Abs(to)
if !strings.HasPrefix(filepath.Join(to, filename), to) { return &IllegalPathError{...} }
```

so `../<username>ZZ/f` lands in a *sibling* directory that still shares the
prefix and **is** written (`file already exists: files/probe_sess_9k2xZZ/px.txt`),
and a zip symlink entry planted the same way (`../<username>S -> /`) makes every
absolute path reachable (`file already exists: files/probe_sess_9k2xS/etc/passwd`).
`writeNewSymbolicLink` does `os.Remove` first, which is the one way to overwrite
despite `OverwriteExisting=false` — and destructive on a shared instance.

The same agent measured the `username` cookie and closed it: every dot-segment
shape answers 500, `/register` forbids `/` and `.`, therefore "the cookie must
name an existing DB row". Every measurement in that sentence is correct and the
conclusion is wrong — the cookie must name an existing **redis key**, and
`PrepareSession` hands out redis keys before checking the password. The lesson is
not "measure more", it is that a negative about an input is only as good as the
*write path* you also read: the cookie was dead until the login handler explained
who fills the map it is looked up in.

## Left on the instance

No delete route exists in either service. Accounts `desirepwn_q7`,
`mainthread_x9`, `probe_sess_9k2x`, `probe_sess_b7qq`, `sane_user_q1`; junk
files under `files/<those>/`; `uploads/<uuid>.*` for every upload; and, from the
files agent, **`files/probe_sess_9k2xS` is a symlink to `/`** — the one artifact
that materially changes the instance, left in place because removing it needs a
write primitive aimed at it.
