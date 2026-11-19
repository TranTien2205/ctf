# Username sources (deep) — building the candidate list

## Tier 1: the guaranteed — owned + seeded

- **your own account** — register one; the guaranteed known-good,
  cannot be locked out of a victim
- **the challenge-named account** — `flag`, `admin`, the challenge name,
  a user named in the description/handout
- **the seeded/default set** — `admin administrator root test demo user
  guest ctf flag service backup deploy system support operator
  monitoring superuser sa`

## Tier 2: the app-leaked — the high-value names

- **the front-end bundle** (`web-source-map`) — `username`, `author`,
  `created_by`, `owner`, `currentUser`, a `{"user":"alice"}` fixture, a
  default `admin` in a config block, a demo/test user in a comment
- **the source/handout** — a `users` table seed, `fixtures.json`,
  `INSERT INTO users`, `admin_user=`, `seed`, a `.sql` dump, a test
  user in a unit test, a git `author`/`committer`
- **public content** — a blog `author=`/`/author/<name>`, a forum
  username, a `/users/`/`/members/` public list, a commenter, a
  `Posted by <name>`, an `admin`'s profile page
- **emails** — a contact/team/`mailto:` page names `alice@corp.com` →
  the `alice`/`alice@corp.com` candidate; the email-prefix is the
  username
- **an IDOR'd object** — a `/api/users/{id}` read names real accounts
- **the error itself** — a debug error that leaks `"user 'admin' ..."`
- **the WP pattern** — `/?author=N` → `/author/<name>/`, a
  `/wp-json/wp/v2/users` list

## Tier 3: the wordlists — bounded, scoped

On an authorized/owned target, a confirmed oracle + a bounded list:

- `SecLists/Usernames/top-usernames-shortlist.txt` (a slice)
- `xato-net-10-million-usernames` — a slice, not the whole
- `cirt.net`, `Names`, `sao`, `burn`, `metasploit` `common_roots`
- the service-specific set — `jenkins gitlab ci sonar nexus vault
  consul prometheus grafana elastic kibana airflow`

**Never** a mass wordlist on a shared/victim target — that is the
abuse the throttle stops. The oracle is proven with 3 requests; the
list is bounded by the throttle measurement.

## The format-normalization set

```
admin   admin@corp.com   corp\admin   admin.corp   a.admin
admin_x   admin-   ADMIN   Admin   'admin'   "admin"   admin\x00
```

Probe the format the app expects; a `404` on the wrong format is a
format, not an oracle.

## The candidate-quality rule

A confirmed account is only useful if it feeds the chain — a `flag`/
`admin`/`service` is high-value; a random `user123` is a target too.
Rank the list by the chain's needs, not the size.
