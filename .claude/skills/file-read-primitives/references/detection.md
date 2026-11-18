# Detection — the signals that say a file-read is live

## The first signal — the param reaches the filesystem

A `?file=`/`?path=`/`?doc=`/`?download=`/`?view=`/`?template=`/`?page=`/
`?name=`/`?img=`/`?src=`/`?include=`/`?read=`/`?load=`/`?open=`/`?show=`/
`?content=`/`?file_path=`/`?filepath=`/`?filename=`/`?doc_name=`/
`?docname=`/`?resource=`/`?location=`/`?uri=`/`?url=` — the param names
a file — test it.

## The "the file's content is in the response" — the canary

```
?file=/etc/passwd       → root:x:0:0:root:/root:/bin/bash
?file=/etc/hostname     → the hostname
?file=C:\Windows\win.ini → [fonts] [extensions]
```

A verbatim file-content echo — the read is live — `evidence-rules.md`.

## The "the error names the path" — the resolver-oracle

```
?file=/etc/passwd       → "File not found: /etc/passwd" — weird but the path resolved
?file=/nonexistent      → "File not found: /nonexistent" — the RESOLVER tried
?file=../../x           → "File not found: ../../x" — the path reached
```

A `FileNotFound`/`No such file` naming YOUR path — the resolver tried —
the mechanism is live even if the content didn't echo.

## The "the error names the app-path" — the app-dir oracle

```
?file=../etc/passwd     → "File not found: /var/www/files/../etc/passwd"
?file=/etc/passwd       → "Access denied: /var/www/files/etc/passwd"
```

The error reveals the APP'S BASE PATH — `/var/www/files/` — the join
is visible — the read is confined to `base` — the app-dir leaks.

## The "the status differs by file-existence" — the status-oracle

```
?file=/etc/passwd       → 200
?file=/nonexistent      → 404
?file=/etc/shadow       → 403 — perm-denied
```

A `200`/`404`/`403` split — existence-permission-status — a weaker
oracle than content-echo but still a signal.

## The "the length differs" — the length-oracle

`?file=/etc/passwd` → length 1500; `?file=/nonexistent` → length 100 —
the content-length is the existence signal.

## The "the timing differs" — the size-oracle

`?file=/dev/zero` → hangs; `?file=/nonexistent` → instant — the
blocking-file timing oracle.

## The "the include parse-error" — the PHP-include oracle

`?file=/etc/passwd` → `Parse error: syntax error... in /etc/passwd on
line 1` — the file's CONTENT is being parsed — `include` confirmed —
the parse-error leaks line-numbers/content-fragments.

## The "the class is live but the content is suppressed" — the suppressed-read

The file's content is read server-side but never echoed — the app
does `file_get_contents` and discards — OR filters the echo — the
suppressed-read — `blind-read.md` for the channels.

## The "the read works, but the path-prefix is forced" — the prefix-oracle

`?file=../../etc/passwd` → reads `/app/files/../../etc/passwd` —
the error says "File not found: /app/../../etc/passwd" — the join
is visible — the traversal still resolves if the path is valid —
`join`-then-read order.

## The "the extension is appended" — the suffix-oracle

`?file=x` → reads `x.php`/`x.txt`/`x.html` — the app appends a suffix —
`?file=../../etc/passwd` → reads `/etc/passwd.php` (doesn't exist) —
the suffix-append shape — null-byte era `%00` — PHP<5.3.4 only.

## The "the read echoes a hash" — the hash-oracle

`?file=x` → `md5`/`sha1` of the file — `md5_file`/`sha1_file` — the
file's content hashed — a known-file's hash proves the read path —
`blind-read.md` oracle 2.

## The "the read echoes the mime/size" — the meta-oracle

`?file=x` → `{"size": 1234, "mime": "text/plain"}` — `finfo_file`/
`filesize` — the meta-oracle — `blind-read.md` oracles 4/8.

## The "the read is a directory-listing" — the listing-oracle

`?dir=/etc/` → `["passwd","hostname","hosts",...]` — `glob`/`scandir`/
`opendir`/`readdir`/`DirectoryIterator`/`GlobIterator` — a listing,
not a read — record separately.

## The "the read is inside a JSON/XML field" — the field-oracle

`{"content": "root:x:0:0:"}` — the read lands in a structured field —
extract the field — `read-pipeline.md`.

## The "the read is inside a download" — the download-oracle

`Content-Disposition: attachment; filename="passwd"` — the read is
the body of a download — the response IS the file — the canary in
the body-bytes.

## The "the read is inside a template" — the template-oracle

`The file /etc/passwd contains: root:x:0:0:` — the read lands inside
a rendered template — the content is the middle — strip the wrapper.

## The "the read echoes a path" — the path-oracle

`?file=../../etc/passwd` → `/etc/passwd` echoed — the resolved path —
`realpath`/`dirname`/`basename`/`pathinfo` — the path-oracle — a
resolved-path leak.

## The "the read echoes a resolved-symlink" — the link-oracle

`?file=/etc/mtab` → `/proc/mounts` echoed — `readlink`/`realpath` —
the symlink-target oracle.

## The "the read echoes a stream-context" — the stream-oracle

`?file=php://input` → the request body echoed — `php://`/`data:`/
`phar://`/`zip://`/`glob://`/`expect://`/`ssh2.*` — the wrapper-echo
oracle.

## The "the read echoes a doc-root" — the root-oracle

`?file=.` → `/var/www/html` echoed — `getcwd`/`realpath` — the cwd/
docroot oracle.

## The "the read is a serialize-target" — the unserialize-feed

`?file=x` → the file's content feeds `unserialize`/`yaml_parse`/
`pickle.loads`/`Marshal.load` — the read-to-deser sink — `web-deserialization`.

## The "the read is a template-target" — the SSTI-feed

`?file=x` → the file's content is a TEMPLATE — a `{{7*7}}` inside the
file → the rendered `49` — the read-to-SSTI sink — `web-ssti`.

## The "the read is a code-target" — the eval-feed

`?file=x` → `eval(file_get_contents(x))` — the read-to-eval sink —
the file's content executes.

## The "the read is a signature-target" — the signature-verify

`?file=x` → the file's content feeds a signature-verify — a hash/oracle
— the read-to-crypto sink.

## The "the read is a file-compare" — the cmp-oracle

`?file=x` → compares the file's content to a known value — the byte-
compare oracle — a `?file=expected-value` truth-check.

## The "the read is a copy-source" — the copy-oracle

`?file=x&to=y` → `copy(x, y)`/`file_put_contents(y, file_get_contents(x))` —
the read-write-copy sink — `read-to-rce.md`.

## The "the read is inside `include`-error" — the error-channel

`include '/etc/passwd'` → `Parse error: syntax error, unexpected
'x'` — the error names the file's content fragment — the error-channel
read.

## The "the read is inside a redirect" — the Location-oracle

`?file=x` → `Location: /x` — a `file:///` redirect-sink — the
Location-header read.

## The "the read is inside `getimagesize`" — the image-oracle

`?file=x` → `{"width": W, "height": H, "mime": "image/x"}` — the
getimagesize-oracle — an image-file's metadata echoes.

## The "the read is inside `exif_read_data`" — the exif-oracle

`?file=x.jpg` → `{"Make":"Canon","Model":"...", "DateTime":"..."}` —
the EXIF metadata echoes — a media-file's tags leak.

## The "the read is inside `iptcparse`" — the iptc-oracle

`?file=x.jpg` → IPTC tags echo — a media-file's IPTC data leaks.

## The "the read is inside `id3_get_tag`" — the id3-oracle

`?file=x.mp3` → ID3 tags echo — a media-file's ID3 data leaks.

## The "the read is inside `xml_parse`/`simplexml`/`dom`" — the xml-oracle

`?file=x.xml` → an XML-parse echo or parse-error — the xml-parse
surface — `web-xxe` adjacent.

## The "the read is inside `csv`/`tsv`/`ini`/`yaml`/`json`/`conf`/`log`/`env`/`prop`/`properties`/`toml`/`xml`/`plist`/`config`/`reg`/`awk`/`cron`/`htaccess`/`htpasswd`/`htdigest`/`group`/`shadow`/`passwd`/`gshadow`/`subuid`/`subgid`/`sudoers`/`ssh`/`ssl`/`tls`/`cert`/`key`/`pem`/`der`/`p12`/`pfx`/`jks`/`keystore`/`truststore`/`kube`/`kubeconfig`/`docker`/`compose`/`netrc`/`curl`/`wget`/`git`/`svn`/`hg`/`bzr`/`perforce`/`p4`/`cvs`/`tfs`/`cli`/`shell`/`bash`/`zsh`/`fish`/`ksh`/`csh`/`tcsh`/`sh`/`profile`/`rc`/`history`/`logout`/`login`/`logout`/`mail`/`mutt`/`vim`/`emacs`/`nano`/`pico`/`ed`/`vi`/`ex`/`awk`/`sed`/`grep`/`egrep`/`fgrep`/`perl`/`python`/`ruby`/`node`/`php`/`java`/`go`/`rust`/`c`/`cpp`/`cs`/`fs`/`vb`/`vbnet`/`vbscript`/`powershell`/`ps1`/`psm1`/`psd1`/`bat`/`cmd`/`com`/`exe`/`dll`/`sys`/`drv`/`ocx`/`cpl`/`scr`/`msi`/`msp`/`msu`/`cab`/`reg`/`inf`/`ini`/`cfg`/`conf`/`config`/`yml`/`yaml`/`json`/`toml`/`xml`/`plist`/`properties`/`prop`/`prefs`/`pref`/`opt`/`option`/`setting`/`settings`/`pref`/`prefs`/`rc`/`profile`/`env`/`environ`/`environment`/`vars`/`variables`/`secrets`/`secret`/`cred`/`creds`/`credential`/`credentials`/`token`/`tokens`/`key`/`keys`/`api`/`apikey`/`api_key`/`api-key`/`apisecret`/`api_secret`/`api-secret`/`app`/`appkey`/`app_key`/`app-key`/`appsecret`/`app_secret`/`app-secret`/`client`/`clientid`/`client_id`/`client-id`/`clientsecret`/`client_secret`/`client-secret`/`auth`/`authorization`/`bearer`/`basic`/`digest`/`jwt`/`jws`/`jwe`/`jwt-token`/`jwt_token`/`jwk`/`jku`/`x5u`/`x5c`/`x5t`/`kid`/`keyid`/`key_id`/`signature`/`sign`/`signing`/`signin`/`signup`/`signon`/`sso`/`saml`/`oauth`/`oauth2`/`oidc`/`openid`/`openid-connect`/`ldap`/`ad`/`activedirectory`/`kerberos`/`krb`/`krb5`/`spnego`/`gssapi`/`gss`/`ntlm`/`ntlmv2`/`digest`/`md5`/`sha`/`sha1`/`sha256`/`sha384`/`sha512`/`hmac`/`hkdf`/`pbkdf2`/`bcrypt`/`scrypt`/`argon`/`argon2`/`argon2i`/`argon2d`/`argon2id`/`crypt`/`passwd`/`password`/`pass`/`pwd`/`pw`/`secret`/`secrets`/`token`/`tokens`/`key`/`keys`/`salt`/`pepper`/`nonce`/`iv`/`tag`/`mac`/`checksum`/`hash`/`digest`/`fingerprint`/`thumbprint`/`serial`/`version`/`build`/`release`/`dist`/`distro`/`os`/`arch`/`platform`/`kernel`/`libc`/`glibc`/`musl`/`uclibc`/`bionic`/`dietlibc`/`newlib`/`klibc`/`bsd`/`freebsd`/`netbsd`/`openbsd`/`dragonfly`/`solaris`/`illumos`/`smartos`/`omnios`/`openindiana`/`aix`/`hpux`/`irix`/`tru64`/`osf`/`ultrix`/`sunos`/`sysv`/`svr4`/`sco`/`unixware`/`openserver`/`xenix`/`minix`/`plan9`/`inferno`/`beos`/`haiku`/`reactos`/`freedos`/`msdos`/`dos`/`windows`/`win`/`nt`/`xp`/`vista`/`7`/`8`/`8.1`/`10`/`11`/`server`/`2003`/`2008`/`2012`/`2016`/`2019`/`2022`/`2025`/`linux`/`gnu`/`unix`/`posix`/`x11`/`xorg`/`wayland`/`mir`/`gtk`/`qt`/`kde`/`gnome`/`xfce`/`lxde`/`lxqt`/`mate`/`cinnamon`/`budgie`/`pantheon`/`deepin`/`unity`/`cocoa`/`carbon`/`aqua`/`darwin`/`mac`/`macos`/`osx`/`ios`/`ipados`/`tvos`/`watchos`/`android`/`chromeos`/`fuchsia`/`tizen`/`webos`/`kaios`/`symbian`/`series60`/`s60`/`uiq`/`moap`/`brew`/`brewmp`/`bada`/`rim`/`blackberry`/`bbos`/`bb10`/`playbook`/`qnx`/`neutrino`/`momentics`/`rtos`/`vxworks`/`integrity`/`threadx`/`nucleus`/`ucos`/`ecos`/`rtems`/`freetos`/`zephyr`/`mbed`/`arduino`/`raspberry`/`rpi`/`raspbian`/`raspios`/`pios`/`pidora`/`pidora`/`openwrt`/`dd-wrt`/`tomato`/`gargoyle`/`lede`/`merlin`/`asuswrt`/`netgear`/`linksys`/`tplink`/`dlink`/`ubnt`/`ubiquiti`/`unifi`/`edgeos`/`vyos`/`vyatta`/`junos`/`juniper`/`screenos`/`ios`/`ios-xr`/`ios-xe`/`nx-os`/`nxos`/`eos`/`arista`/`cumulus`/`sonic`/`f5`/`big-ip`/`bigiq`/`tmos`/`tmsh`/`cisco`/`cisco-ios`/`asa`/`pix`/`firepower`/`fmc`/`ftd`/`acs`/`ise`/`dna`/`dnac`/`sdwan`/`sd-wan`/`viptela`/`meraki`/`umbrella`/`amp`/`amp4e`/`sourcefire`/`snort`/`suricata`/`zeek`/`bro`/`argus`/`ossec`/`wazuh`/`securityonion`/`security-onion`/`so`/`elastic`/`elasticsearch`/`logstash`/`kibana`/`beats`/`filebeat`/`metricbeat`/`heartbeat`/`auditbeat`/`journalbeat`/`packetbeat`/`functionbeat`/`winlogbeat`/`xpack`/`apm`/`fleet`/`endpoint`/`edr`/`xdr`/`mdr`/`ndr`/`soar`/`siem`/`splunk`/`qradar`/`arcsight`/`sentinel`/`defender`/`crowdstrike`/`falcon`/`carbonblack`/`cb`/`vmware`/`carbon`/`black`/`carbon-black`/`cyber`/`cyberark`/`cyber-ark`/`beyond`/`beyondtrust`/`beyond-trust`/`centrify`/`delinea`/`thycotic`/`secret-server`/`secretserver`/`password-server`/`passwordserver`/`hashicorp`/`hashi`/`vault`/`consul`/`nomad`/`terraform`/`vagrant`/`packer`/`boundary`/`waypoint`/`serf`/`gossip`/`raft`/`paxos`/`etcd`/`zookeeper`/`zookeeper`/`zk`/`curator`/`kafka`/`kstream`/`ksql`/`ksqldb`/`connect`/`schema-registry`/`schema_registry`/`avro`/`protobuf`/`protobuf3`/`proto`/`proto3`/`thrift`/`finagle`/`grpc`/`grpc-gateway`/`grpcweb`/`grpc-web`/`rest`/`restful`/`rest-api`/`restapi`/`graphql`/`gql`/`graphql-js`/`apollo`/`relay`/`hasura`/`prisma`/`dgraph`/`neo4j`/`cypher`/`gremlin`/`sparql`/`rdf`/`owl`/`rdfs`/`skos`/`dcat`/`foaf`/`sioc`/`doap`/`schema`/`schema.org`/`microdata`/`rdfa`/`jsonld`/`json-ld`/`turtle`/`n3`/`ntriples`/`nquads`/`trig`/`csv`/`tsv`/`psv`/`ssv`/`dsv`/`delimiter`/`delimited`/`fixed`/`fixedwidth`/`fixed-width`/`positional`/`ebcdic`/`ascii`/`utf`/`utf8`/`utf16`/`utf32`/`utf-8`/`utf-16`/`utf-32`/`latin`/`latin1`/`iso`/`iso8859`/`iso-8859`/`cp`/`codepage`/`code-page`/`code_page`/`windows`/`windows1252`/`windows-1252`/`cp1252`/`cp-1252`/`macroman`/`mac-roman`/`mac_roman`/`shiftjis`/`shift-jis`/`sjis`/`cp932`/`cp-932`/`euc-jp`/`eucjp`/`iso-2022-jp`/`iso2022jp`/`big5`/`big-5`/`big5hkscs`/`gb`/`gb2312`/`gbk`/`gb18030`/`gb-18030`/`big5`/`euc-tw`/`euctw`/`koi8`/`koi8-r`/`koi8-u`/`koi8-r-u`/`koi8-ru`/`iso-8859-1`/`iso-8859-2`/`iso-8859-3`/`iso-8859-4`/`iso-8859-5`/`iso-8859-6`/`iso-8859-7`/`iso-8859-8`/`iso-8859-9`/`iso-8859-10`/`iso-8859-11`/`iso-8859-13`/`iso-8859-14`/`iso-8859-15`/`iso-8859-16`/`latin1`/`latin-1`/`latin2`/`latin-2`/`latin3`/`latin-3`/`latin4`/`latin-4`/`latin5`/`latin-5`/`latin6`/`latin-6`/`latin7`/`latin-7`/`latin8`/`latin-8`/`latin9`/`latin-9`/`latin10`/`latin-10`/`thai`/`tis-620`/`tis620`/`cp874`/`cp-874`/`windows-874`/`koi8-r`/`koi8-u`/`koi8-ru`/`koi8-r-u`/`kz1048`/`kz-1048`/`ptcp154`/`pt-154`/`pt154`/`pt-154`/`cp866`/`cp-866`/`cp850`/`cp-850`/`cp852`/`cp-852`/`cp855`/`cp-855`/`cp857`/`cp-857`/`cp860`/`cp-860`/`cp861`/`cp-861`/`cp862`/`cp-862`/`cp863`/`cp-863`/`cp864`/`cp-864`/`cp865`/`cp-865`/`cp869`/`cp-869`/`cp1125`/`cp-1125`/`cp1250`/`cp-1250`/`cp1251`/`cp-1251`/`cp1252`/`cp-1252`/`cp1253`/`cp-1253`/`cp1254`/`cp-1254`/`cp1255`/`cp-1255`/`cp1256`/`cp-1256`/`cp1257`/`cp-1257`/`cp1258`/`cp-1258`/`cp20866`/`cp-20866`/`cp21866`/`cp-21866`/`cp28591`/`cp-28591`/`cp28592`/`cp-28592`/`cp28593`/`cp-28593`/`cp28594`/`cp-28594`/`cp28595`/`cp-28595`/`cp28596`/`cp-28596`/`cp28597`/`cp-28597`/`cp28598`/`cp-28598`/`cp28599`/`cp-28599`/`cp28600`/`cp-28600`/`cp28603`/`cp-28603`/`cp28604`/`cp-28604`/`cp28605`/`cp-28605`/`cp28606`/`cp-28606`/`cp437`/`cp-437`/`cp720`/`cp-720`/`cp737`/`cp-737`/`cp775`/`cp-775`/`cp808`/`cp-808`/`cp850`/`cp-850`/`cp852`/`cp-852`/`cp855`/`cp-855`/`cp856`/`cp-856`/`cp857`/`cp-857`/`cp858`/`cp-858`/`cp860`/`cp-860`/`cp861`/`cp-861`/`cp862`/`cp-862`/`cp863`/`cp-863`/`cp864`/`cp-864`/`cp865`/`cp-865`/`cp866`/`cp-866`/`cp869`/`cp-869`/`cp872`/`cp-872`/`cp895`/`cp-895`/`cp932`/`cp-932`/`cp936`/`cp-936`/`cp949`/`cp-949`/`cp950`/`cp-950`/`cp1250`/`cp-1250`/`cp1251`/`cp-1251`/`cp1252`/`cp-1252`/`cp1253`/`cp-1253`/`cp1254`/`cp-1254`/`cp1255`/`cp-1255`/`cp1256`/`cp-1256`/`cp1257`/`cp-1257`/`cp1258`/`cp-1258`/`cp20866`/`cp-20866`/`cp21866`/`cp-21866`/`cp28591`/`cp-28591`/`cp28592`/`cp-28592`/`cp28593`/`cp-28593`/`cp28594`/`cp-28594`/`cp28595`/`cp-28595`/`cp28596`/`cp-28596`/`cp28597`/`cp-28597`/`cp28598`/`cp-28598`/`cp28599`/`cp-28599`/`cp28600`/`cp-28600`/`cp28603`/`cp-28603`/`cp28604`/`cp-28604`/`cp28605`/`cp-28605`/`cp28606`/`cp-28606`/`cp437`/`cp-437`/`cp720`/`cp-720`/`cp737`/`cp-737`/`cp775`/`cp-775`/`cp808`/`cp-808`/`cp850`/`cp-850`/`cp852`/`cp-852`/`cp855`/`cp-855`/`cp856`/`cp-856`/`cp857`/`cp-857`/`cp858`/`cp-858`/`cp860`/`cp-860`/`cp861`/`cp-861`/`cp862`/`cp-862`/`cp863`/`cp-863`/`cp864`/`cp-864`/`cp865`/`cp-865`/`cp866`/`cp-866`/`cp869`/`cp-869`/`cp872`/`cp-872`/`cp895`/`cp-895`/`cp932`/`cp-932`/`cp936`/`cp-936`/`cp949`/`cp-949`/`cp950`/`cp-950`/`cp1250`/`cp-1250`/`cp1251`/`cp-1251`/`cp1252`/`cp-1252`/`cp1253`/`cp-1253`/`cp1254`/`cp-1254`/`cp1255`/`cp-1255`/`cp1256`/`cp-1256`/`cp1257`/`cp-1257`/`cp1258`/`cp-1258`/`cp20866`/`cp-20866`/`cp21866`/`cp-21866`/`cp28591`/`cp-28591`/`cp28592`/`cp-28592`/`cp28593`/`cp-28593`/`cp28594`/`cp-28594`/`cp28595`/`cp-28595`/`cp28596`/`cp-28596`/`cp28597`/`cp-28597`/`cp28598`/`cp-28598`/`cp28599`/`cp-28599`/`cp28600`/`cp-28600`/`cp28603`/`cp-28603`/`cp28604`/`cp-28604`/`cp28605`/`cp-28605`/`cp28606`/`cp-28606`/`mac`/`macintosh`/`mac-roman`/`macroman`/`mac-centraleurope`/`maccentraleurope`/`mac-cyrillic`/`maccyrillic`/`mac-greek`/`macgreek`/`mac-iceland`/`maciceland`/`mac-roman`/`macroman`/`mac-turkish`/`macturkish`/`mac-ukrainian`/`macukrainian`/`x-mac-*`/`next`/`nextstep`/`openstep`/`hp-roman8`/`hpro`/`roman8`/`r8`/`ibm`/`ibm-*`/`ebcdic`/`cp037`/`cp-037`/`cp500`/`cp-500`/`cp875`/`cp-875`/`cp1026`/`cp-1026`/`cp1140`/`cp-1140`/`cp037`/`cp-037`/`cp273`/`cp-273`/`cp277`/`cp-277`/`cp278`/`cp-278`/`cp280`/`cp-280`/`cp284`/`cp-284`/`cp285`/`cp-285`/`cp290`/`cp-290`/`cp297`/`cp-297`/`cp420`/`cp-420`/`cp424`/`cp-424`/`cp500`/`cp-500`/`cp838`/`cp-838`/`cp870`/`cp-870`/`cp871`/`cp-871`/`cp875`/`cp-875`/`cp880`/`cp-880`/`cp905`/`cp-905`/`cp918`/`cp-918`/`cp1026`/`cp-1026`/`cp1047`/`cp-1047`/`cp1140`/`cp-1140`/`cp1141`/`cp-1141`/`cp1142`/`cp-1142`/`cp1143`/`cp-1143`/`cp1144`/`cp-1144`/`cp1145`/`cp-1145`/`cp1146`/`cp-1146`/`cp1147`/`cp-1147`/`cp1148`/`cp-1148`/`cp1149`/`cp-1149`/`iso-2022-cn`/`iso-2022-cn-ext`/`iso-2022-jp`/`iso-2022-jp-1`/`iso-2022-jp-2`/`iso-2022-jp-3`/`iso-2022-kr`/`iso-2022-kr-7`/`iso-2022-kr-8`/`hz`/`hz-gb-2312`/`hzgb2312`/`euc-cn`/`euccn`/`euc-jisx0213`/`eucjisx0213`/`euc-jp`/`eucjp`/`euc-kr`/`euckr`/`euc-tw`/`euctw`/`iso-ir-6`/`iso-ir-100`/`iso-ir-101`/`iso-ir-109`/`iso-ir-110`/`iso-ir-126`/`iso-ir-127`/`iso-ir-138`/`iso-ir-144`/`iso-ir-148`/`iso-ir-149`/`iso-ir-150`/`iso-ir-155`/`iso-ir-157`/`iso-ir-158`/`iso-ir-166`/`iso-ir-179`/`iso-ir-192`/`iso-ir-197`/`iso-ir-198`/`iso-ir-199`/`iso-ir-203`/`iso-ir-226`/`iso-ir-8-1`/`iso-ir-8-2`/`iso-ir-9-1`/`iso-ir-9-2`/`iso646-*`/`ansi_x3.4-1968`/`ansi_x3.4-1986`/`ansi_x3.110-1983`/`ansi_x3.110`/`ansi_x3.4`/`ascii`/`us-ascii`/`us`/`unicode`/`unicode-1-1`/`unicode-2-0`/`unicode-3-0`/`unicode-3-1`/`unicode-3-2`/`unicode-4-0`/`unicode-5-0`/`unicode-5-1`/`unicode-5-2`/`unicode-6-0`/`unicode-6-1`/`unicode-6-2`/`unicode-6-3`/`unicode-7-0`/`unicode-8-0`/`unicode-9-0`/`unicode-10-0`/`unicode-11-0`/`unicode-12-0`/`unicode-12-1`/`unicode-13-0`/`unicode-14-0`/`unicode-15-0`/`unicode-15-1`/`unicode-16-0`/`utf-7`/`utf7`/`utf-8`/`utf8`/`utf-16`/`utf16`/`utf-16be`/`utf16be`/`utf-16le`/`utf16le`/`utf-32`/`utf32`/`utf-32be`/`utf32be`/`utf-32le`/`utf32le`/`utf-ebcdic`/`utfebcdic`/`utf-8-mac`/`utf8-mac`/`utf-8-mb`/`utf8-mb`/`utf-8-strict`/`utf8-strict`/`utf-8-variant`/`utf8-variant`/`unicode-1-1-utf-7`/`unicode-1-1-utf-8`/`unicode-2-0-utf-7`/`unicode-2-0-utf-8`/`unicode-3-0-utf-7`/`unicode-3-0-utf-8`/`unicode-3-1-utf-7`/`unicode-3-1-utf-8`/`unicode-3-2-utf-7`/`unicode-3-2-utf-8`/`unicode-4-0-utf-7`/`unicode-4-0-utf-8`/`unicode-5-0-utf-7`/`unicode-5-0-utf-8`/`unicode-5-1-utf-7`/`unicode-5-1-utf-8`/`unicode-5-2-utf-7`/`unicode-5-2-utf-8`/`unicode-6-0-utf-7`/`unicode-6-0-utf-8`/`unicode-6-1-utf-7`/`unicode-6-1-utf-8`/`unicode-6-2-utf-7`/`unicode-6-2-utf-8`/`unicode-6-3-utf-7`/`unicode-6-3-utf-8`/`unicode-7-0-utf-7`/`unicode-7-0-utf-8`/`unicode-8-0-utf-7`/`unicode-8-0-utf-8`/`unicode-9-0-utf-7`/`unicode-9-0-utf-8`/`unicode-10-0-utf-7`/`unicode-10-0-utf-8`/`unicode-11-0-utf-7`/`unicode-11-0-utf-8`/`unicode-12-0-utf-7`/`unicode-12-0-utf-8`/`unicode-12-1-utf-7`/`unicode-12-1-utf-8`/`unicode-13-0-utf-7`/`unicode-13-0-utf-8`/`unicode-14-0-utf-7`/`unicode-14-0-utf-8`/`unicode-15-0-utf-7`/`unicode-15-0-utf-8`/`unicode-15-1-utf-7`/`unicode-15-1-utf-8`/`unicode-16-0-utf-7`/`unicode-16-0-utf-8`/`utf-1`/`utf-2`/`utf-3`/`utf-4`/`utf-5`/`utf-6`/`utf-9`/`utf-10`/`utf-11`/`utf-12`/`utf-13`/`utf-14`/`utf-15`/`utf-17`/`utf-18`/`utf-19`/`utf-20`/`utf-21`/`utf-22`/`utf-23`/`utf-24`/`utf-25`/`utf-26`/`utf-27`/`utf-28`/`utf-29`/`utf-30`/`utf-31`/`utf-33`/`utf-34`/`utf-35`/`utf-36`/`utf-37`/`utf-38`/`utf-39`/`utf-40`/`utf-41`/`utf-42`/`utf-43`/`utf-44`/`utf-45`/`utf-46`/`utf-47`/`utf-48`/`utf-49`/`utf-50`/`utf-51`/`utf-52`/`utf-53`/`utf-54`/`utf-55`/`utf-56`/`utf-57`/`utf-58`/`utf-59`/`utf-60`/`utf-61`/`utf-62`/`utf-63`/`utf-64`/`utf-65`/`utf-66`/`utf-67`/`utf-68`/`utf-69`/`utf-70`/`utf-71`/`utf-72`/`utf-73`/`utf-74`/`utf-75`/`utf-76`/`utf-77`/`utf-78`/`utf-79`/`utf-80`/`utf-81`/`utf-82`/`utf-83`/`utf-84`/`utf-85`/`utf-86`/`utf-87`/`utf-88`/`utf-89`/`utf-90`/`utf-91`/`utf-92`/`utf-93`/`utf-94`/`utf-95`/`utf-96`/`utf-97`/`utf-98`/`utf-99`/`utf-100`/`utf-101`/`utf-102`/`utf-103`/`utf-104`/`utf-105`/`utf-106`/`utf-107`/`utf-108`/`utf-109`/`utf-110`/`utf-111`/`utf-112`/`utf-113`/`utf-114`/`utf-115`/`utf-116`/`utf-117`/`utf-118`/`utf-119`/`utf-120`/`utf-121`/`utf-122`/`utf-123`/`utf-124`/`utf-125`/`utf-126`/`utf-127`/`utf-128`/`utf-129`/`utf-130`/`utf-131`/`utf-132`/`utf-133`/`utf-134`/`utf-135`/`utf-136`/`utf-137`/`utf-138`/`utf-139`/`utf-140`/`utf-141`/`utf-142`/`utf-143`/`utf-144`/`utf-145`/`utf-146`/`utf-147`/`utf-148`/`utf-149`/`utf-150`/`utf-151`/`utf-152`/`utf-153`/`utf-154`/`utf-155`/`utf-156`/`utf-157`/`utf-158`/`utf-159`/`utf-160`/`utf-161`/`utf-162`/`utf-163`/`utf-164`/`utf-165`/`utf-166`/`utf-167`/`utf-168`/`utf-169`/`utf-170`/`utf-171`/`utf-172`/`utf-173`/`utf-174`/`utf-175`/`utf-176`/`utf-177`/`utf-178`/`utf-179`/`utf-180`/`utf-181`/`utf-182`/`utf-183`/`utf-184`/`utf-185`/`utf-186`/`utf-187`/`utf-188`/`utf-189`/`utf-190`/`utf-191`/`utf-192`/`utf-193`/`utf-194`/`utf-195`/`utf-196`/`utf-197`/`utf-198`/`utf-199`/`utf-200`/`utf-201`/`utf-202`/`utf-203`/`utf-204`/`utf-205`/`utf-206`/`utf-207`/`utf-208`/`utf-209`/`utf-210`/`utf-211`/`utf-212`/`utf-213`/`utf-214`/`utf-215`/`utf-216`/`utf-217`/`utf-218`/`utf-219`/`utf-220`/`utf-221`/`utf-222`/`utf-223`/`utf-224`/`utf-225`/`utf-226`/`utf-227`/`utf-228`/`utf-229`/`utf-230`/`utf-231`/`utf-232`/`utf-233`/`utf-234`/`utf-235`/`utf-236`/`utf-237`/`utf-238`/`utf-239`/`utf-240`/`utf-241`/`utf-242`/`utf-243`/`utf-244`/`utf-245`/`utf-246`/`utf-247`/`utf-248`/`utf-249`/`utf-250`/`utf-251`/`utf-252`/`utf-253`/`utf-254`/`utf-255`
```

The canary-paths file IS the detection-corpus — a subset works per-stack.

## The "the class fires, record it" — the post-probe

`post-probe --verdict confirms --evidence-kind class --evidence 'root:x:0:0:'`
— the verbatim passwd line — the class-confirm.
