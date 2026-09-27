# web-xs-leaks — techniques reported in public CTF writeups

**This is published knowledge, not local experience.** Nothing here was solved
in this repository. `evidence_level` for this class stays `catalogue` and
this class's field notes stay a template stub on purpose: that stub is the
honest backlog of classes nothing here has solved.
Every claim below carries the writeup URL it came from and a verbatim span
from the fetched page. A writeup's own claim is not verification.

Source: 18,493-URL public writeup catalog, fetched and distilled
2026-09-26; each card was checked by a second pass that rejected 48 of 150.


## 1. Read window.frames.length of a cross-origin page held in an iframe: a search page that renders one nested frame per matching record turns the frame count into a boolean hit/miss oracle for the attacker's query.

- **status**: `writeup-claimed` — no target was probed for this here
- **why it works**: The frame count of a cross-origin window is readable without violating the same-origin policy, and the target ships no X-Frame-Options or frame-ancestors, so the victim's credentialed search-results page can be embedded and its per-result frames counted even though its body cannot be read.
- **first probe**: On an attacker page, point one iframe at the search endpoint with a substring that must match the victim's data and read iframe.contentWindow.frames.length inside the iframe's onload handler; repeat with a substring that cannot match.
- **expected signal**: frames.length is greater than zero for the matching query and zero for the non-matching one, read from the embedding page with no cross-origin access error.
- **falsifier**: The frame is refused (X-Frame-Options / frame-ancestors), or frames.length is identical for a guaranteed match and a guaranteed miss, meaning results are not rendered one frame per hit.
- **sources** (2):
  - Facebook CTF 2019 — https://blog.pspaul.de/posts/facebook-ctf-2019-secret-note-keeper
    > using the `window.frames.length` property in an iframe to determine if notes are present
  - Facebook CTF 2019 — https://blog.pspaul.de/posts/facebook-ctf-2019-secret-note-keeper
    > <!doctype html > < html > < head > < title > XS-Leaker </ title > </ head > < body > < iframe id

## 2. Extend a known secret prefix one character at a time by re-pointing a boolean search oracle at prefix+candidate and re-submitting the attacker page to the application's own report/visit endpoint, so the logged-in bot re-runs the oracle once per candidate.

- **status**: `writeup-claimed` — no target was probed for this here
- **why it works**: The search matches a substring of the victim's own records, so prefix+correct-char stays a hit while prefix+wrong-char becomes a miss; the bug-report feature supplies an authenticated visit to any attacker URL, and the bot carries the victim's session cookie into the oracle request.
- **first probe**: Submit one report whose link is an attacker page hard-coded to a prefix known to be present in the victim's data, then a second report with that prefix plus a character that cannot occur, and compare the two callbacks in the attacker log.
- **expected signal**: Exactly one of the two reports produces the positive-side callback, and the callback query string carries the prefix under test so each round is attributable.
- **falsifier**: Both candidates land on the same side of the oracle, or no request from the bot ever reaches the attacker page, meaning the submitted link is not visited with the victim's session.
- **sources** (4):
  - Facebook CTF 2019 — https://s1r1uss.blogspot.com/2019/06/facebook-ctf-2019-writeup_2.html#product
    > iterate = 'iterate.txt' ; while read c1;
  - Facebook CTF 2019 — https://s1r1uss.blogspot.com/2019/06/facebook-ctf-2019-writeup_2.html#product
    > hash = "$(go run pow.go $data)" ; echo "${hash}" ; flag = "fb{cr055_s173_L34|<5_4r" ;
  - Facebook CTF 2019 — https://s1r1uss.blogspot.com/2019/06/facebook-ctf-2019-writeup_2.html#product
    > curl "http://challenges.fbctf.com:8082/report_bugs" -X POST --data "title=msrk&body=msrk&link=http://987bd815.ngrok.io/fbctf/index.
  - Securinets CTF Quals 2022 — https://blog.bi0s.in/2022/04/14/Web/NarutoKeeper-SecurinetsCTFQuals2022
    > Exploitable via a crafted query on the /search endpoint to leak flag data

## 3. Use the victim browser's history as the oracle: a search URL whose response was 404 never enters history, so rendering that exact URL as a link and measuring the cost of a forced repaint of its :visited styling separates 'the search matched' from 'it did not'.

- **status**: `writeup-claimed` — no target was probed for this here
- **why it works**: Only a non-404 navigation is recorded in history, and although :visited styling cannot be read directly because of the styling restrictions, the repaint cost of an expensive style applied to a visited link differs measurably from the same style on a known-unvisited control URL.
- **first probe**: Have the victim navigate the search URL for one candidate query, then from the attacker page render a link to that exact URL alongside a control URL that was never visited, apply the heavy style and compare the two repaint timings.
- **expected signal**: The repaint measurement for the searched URL separates cleanly from the control URL's and tracks whether that query matched, repeating across candidates.
- **falsifier**: The two URLs measure the same after a navigation known to have returned 200, or the 404 path also enters history, so visited state carries no information about the match.
- **sources** (4):
  - TeamItaly CTF 2023 — https://github.com/TeamItaly/TeamItalyCTF-2023/blob/master/leakynotev3/README.md
    > a way to leak headless history. How we can do that? Do you know the `:visited` selector?
  - TeamItaly CTF 2023 — https://github.com/TeamItaly/TeamItalyCTF-2023/blob/master/leakynotev3/README.md
    > f the bot visits a link whose result is 404 it will not be styled as `:visited`
  - TeamItaly CTF 2023 — https://github.com/TeamItaly/TeamItalyCTF-2023/blob/master/leakynotev3/README.md
    > we can force the browser to apply complex CSS repaint operations to `:visited` links and we can compare performance measurements with those taken for a known-unvisited "control" URL
  - TeamItaly CTF 2023 — https://github.com/TeamItaly/TeamItalyCTF-2023/blob/master/leakynotev3/README.md
    > a 404 oracle exploitation through CSS `:visited` selector and performance measurement
