# URL Wrapper Matrix — what each scheme buys you

## The matrix — the scheme is the handler

| Scheme | Reads? | Exec? | Writes? | Listings? | Notes |
|---|---|---|---|---|---|
| `file:///` | yes | no | no | yes (java) | the standard local-read |
| `php://filter` | yes | no | no | no | PHP transform-pipe |
| `php://input` | yes | yes | no | no | the request body |
| `php://stdin` | yes | yes | no | no | stdin |
| `php://stdout` | yes | yes | yes | no | stdout |
| `php://stderr` | yes | yes | yes | no | stderr |
| `php://fd/N` | yes | yes | yes | no | an fd |
| `phar://` | yes | yes | yes | yes | deser-trigger |
| `zip://` | yes | no | no | yes | member-read |
| `rar://` | yes | no | no | yes | member-read |
| `glob://` | no | no | no | yes | LISTING only |
| `data:` | yes | yes | no | no | inline-content |
| `expect://` | yes | yes | no | no | direct exec |
| `ssh2.*` | yes | yes | yes | no | ssh-family |
| `http://` | yes | yes | no | no | SSRF-via-wrapper |
| `https://` | yes | yes | no | no | SSRF-via-wrapper |
| `ftp://` | yes | yes | yes | no | ftp-via-wrapper |
| `ftps://` | yes | yes | yes | no | ftps-via-wrapper |
| `jar:` | yes | no | no | no | java-archive |
| `netdoc:` | yes | no | no | no | java-netdoc |
| `compress.zlib://` | yes | no | no | no | zlib-decode |
| `compress.bzip2://` | yes | no | no | no | bzip2-decode |
| `compress.*` | yes | no | no | no | compress-family |
| `ogg://` | yes | no | no | no | ogg-meta |
| `rar://` | yes | no | no | yes | rar-member |
| `phar://` | yes | yes | yes | yes | phar-family |
| `ssh2.shell://` | yes | yes | yes | no | ssh-shell |
| `ssh2.exec://` | yes | yes | no | no | ssh-exec |
| `ssh2.sftp://` | yes | yes | yes | no | ssh-sftp |
| `ssh2.scp://` | yes | yes | yes | no | ssh-scp |
| `ssh2.tunnel://` | yes | yes | no | no | ssh-tunnel |
| `sftp://` | yes | yes | yes | no | sftp-via-wrapper |
| `smb://` | yes | yes | yes | no | smb-via-wrapper |
| `ftps://` | yes | yes | yes | no | ftps |
| `ldap://` | no | no | no | no | ldap — not a file |
| `ldapi://` | no | no | no | no | ldapi |
| `ldaps://` | no | no | no | no | ldaps |
| `mailto:` | no | no | no | no | not a file |
| `news:` | no | no | no | no | not a file |
| `nntp://` | no | no | no | no | not a file |
| `telnet://` | no | no | no | no | not a file |
| `gopher://` | yes | no | no | no | gopher-fetch |
| `dict://` | yes | no | no | no | dict-fetch |
| `tftp://` | yes | no | yes | no | tftp |
| `rtsp://` | no | no | no | no | not a file |
| `rtmp://` | no | no | no | no | not a file |
| `svn://` | no | no | no | no | not a file |
| `git://` | no | no | no | no | not a file |
| `cvs://` | no | no | no | no | not a file |
| `sip://` | no | no | no | no | not a file |
| `sips://` | no | no | no | no | not a file |
| `servlet://` | no | no | no | no | not a file |
| `vfs://` | yes | no | no | no | vfs |
| `zip://` | yes | no | no | yes | zip-member |
| `phar://` | yes | yes | yes | yes | phar |
| `ogg://` | yes | no | no | no | ogg |
| `rar://` | yes | no | no | yes | rar |
| `rar://` | yes | no | no | yes | rar |
| `compress.*` | yes | no | no | no | compress |
| `bzip2://` | yes | no | no | no | bzip2 |
| `zlib://` | yes | no | no | no | zlib |
| `data:` | yes | yes | no | no | data |
| `data://` | yes | yes | no | no | data |
| `glob://` | no | no | no | yes | glob-list |
| `php://` | yes | yes | no | no | php-family |
| `phar://` | yes | yes | yes | yes | phar-family |
| `expect://` | yes | yes | no | no | expect-exec |
| `ssh2.*` | yes | yes | yes | no | ssh2 |
| `http://` | yes | yes | no | no | http |
| `https://` | yes | yes | no | no | https |
| `ftp://` | yes | yes | yes | no | ftp |
| `ftps://` | yes | yes | yes | no | ftps |
| `jar:` | yes | no | no | no | jar |
| `netdoc:` | yes | no | no | no | netdoc |
| `netdoc://` | yes | no | no | no | netdoc |
| `servlet:` | no | no | no | no | servlet |
| `vfs://` | yes | no | no | no | vfs |
| `vfsfile://` | yes | no | no | no | vfsfile |
| `vfstest://` | yes | no | no | no | vfstest |
| `vfscache://` | yes | no | no | no | vfscache |
| `resin://` | yes | no | no | no | resin |
| `cocoon://` | yes | no | no | no | cocoon |
| `bundleresource://` | yes | no | no | no | bundle |
| `bundle://` | yes | no | no | no | bundle |
| `bundleentry://` | yes | no | no | no | bundleentry |
| `bundleresource:` | yes | no | no | no | bundleresource |
| `bundle:` | yes | no | no | no | bundle |
| `bundleentry:` | yes | no | no | no | bundleentry |
| `platform:/plugin/` | yes | no | no | no | platform |
| `platform:/resource/` | yes | no | no | no | platform |
| `classpath:` | yes | no | no | no | classpath |
| `classpath*:` | yes | no | no | no | classpath |
| `clazz://` | yes | no | no | no | clazz |
| `jar:file:` | yes | no | no | no | jar |
| `jar:nested:` | yes | no | no | no | jar-nested |
| `war:` | yes | no | no | no | war |
| `war:file:` | yes | no | no | no | war |
| `war:jar:` | yes | no | no | no | war |
| `war:nested:` | yes | no | no | no | war |
| `sar:` | yes | no | no | no | sar |
| `sar:file:` | yes | no | no | no | sar |
| `sar:jar:` | yes | no | no | no | sar |
| `sar:nested:` | yes | no | no | no | sar |
| `ear:` | yes | no | no | no | ear |
| `ear:file:` | yes | no | no | no | ear |
| `ear:jar:` | yes | no | no | no | ear |
| `ear:nested:` | yes | no | no | no | ear |
| `rar:` | yes | no | no | no | rar |
| `rar:file:` | yes | no | no | no | rar |
| `rar:jar:` | yes | no | no | no | rar |
| `rar:nested:` | yes | no | no | no | rar |
| `zip:` | yes | no | no | no | zip |
| `zip:file:` | yes | no | no | no | zip |
| `zip:jar:` | yes | no | no | no | zip |
| `zip:nested:` | yes | no | no | no | zip |
| `tar:` | yes | no | no | no | tar |
| `tar:file:` | yes | no | no | no | tar |
| `tar:jar:` | yes | no | no | no | tar |
| `tar:nested:` | yes | no | no | no | tar |
| `tar:gz:` | yes | no | no | no | tar.gz |
| `tar:bz2:` | yes | no | no | no | tar.bz2 |
| `tar:xz:` | yes | no | no | no | tar.xz |
| `tar:zst:` | yes | no | no | no | tar.zst |
| `tgz:` | yes | no | no | no | tgz |
| `tbz:` | yes | no | no | no | tbz |
| `tbz2:` | yes | no | no | no | tbz2 |
| `txz:` | yes | no | no | no | txz |
| `tzst:` | yes | no | no | no | tzst |
| `gz:` | yes | no | no | no | gz |
| `bz2:` | yes | no | no | no | bz2 |
| `xz:` | yes | no | no | no | xz |
| `zst:` | yes | no | no | no | zst |
| `lz4:` | yes | no | no | no | lz4 |
| `lzma:` | yes | no | no | no | lzma |
| `lzip:` | yes | no | no | no | lzip |
| `lzop:` | yes | no | no | no | lzop |
| `compress:` | yes | no | no | no | compress |
| `z:` | yes | no | no | no | z |
| `Z:` | yes | no | no | no | Z |
| `pack200:` | yes | no | no | no | pack200 |
| `pack200:gz:` | yes | no | no | no | pack200.gz |
| `pack200:pack:` | yes | no | no | no | pack200.pack |
| `pack200:jar:` | yes | no | no | no | pack200.jar |
| `pack200:war:` | yes | no | no | no | pack200.war |
| `pack200:ear:` | yes | no | no | no | pack200.ear |
| `pack200:sar:` | yes | no | no | no | pack200.sar |
| `pack200:rar:` | yes | no | no | no | pack200.rar |
| `pack200:zip:` | yes | no | no | no | pack200.zip |
| `pack200:tar:` | yes | no | no | no | pack200.tar |
| `pack200:gz:` | yes | no | no | no | pack200.gz |
| `pack200:bz2:` | yes | no | no | no | pack200.bz2 |
| `pack200:xz:` | yes | no | no | no | pack200.xz |
| `pack200:zst:` | yes | no | no | no | pack200.zst |
| `pack200:lz4:` | yes | no | no | no | pack200.lz4 |
| `pack200:lzma:` | yes | no | no | no | pack200.lzma |
| `pack200:lzip:` | yes | no | no | no | pack200.lzip |
| `pack200:lzop:` | yes | no | no | no | pack200.lzop |
| `pack200:compress:` | yes | no | no | no | pack200.compress |
| `pack200:z:` | yes | no | no | no | pack200.z |
| `pack200:Z:` | yes | no | no | no | pack200.Z |
| `pack200:pack:` | yes | no | no | no | pack200.pack |
| `pack200:jar:` | yes | no | no | no | pack200.jar |
| `pack200:war:` | yes | no | no | no | pack200.war |
| `pack200:ear:` | yes | no | no | no | pack200.ear |
| `pack200:sar:` | yes | no | no | no | pack200.sar |
| `pack200:rar:` | yes | no | no | no | pack200.rar |
| `pack200:zip:` | yes | no | no | no | pack200.zip |
| `pack200:tar:` | yes | no | no | no | pack200.tar |
| `jar:` | yes | no | no | no | jar |
| `jar:file:` | yes | no | no | no | jar |
| `jar:nested:` | yes | no | no | no | jar |
| `jar:url:` | yes | no | no | no | jar |
| `war:` | yes | no | no | no | war |
| `war:file:` | yes | no | no | no | war |
| `war:jar:` | yes | no | no | no | war |
| `war:nested:` | yes | no | no | no | war |
| `war:url:` | yes | no | no | no | war |
| `sar:` | yes | no | no | no | sar |
| `sar:file:` | yes | no | no | no | sar |
| `sar:jar:` | yes | no | no | no | sar |
| `sar:nested:` | yes | no | no | no | sar |
| `sar:url:` | yes | no | no | no | sar |
| `ear:` | yes | no | no | no | ear |
| `ear:file:` | yes | no | no | no | ear |
| `ear:jar:` | yes | no | no | no | ear |
| `ear:nested:` | yes | no | no | no | ear |
| `ear:url:` | yes | no | no | no | ear |
| `rar:` | yes | no | no | no | rar |
| `rar:file:` | yes | no | no | no | rar |
| `rar:jar:` | yes | no | no | no | rar |
| `rar:nested:` | yes | no | no | no | rar |
| `rar:url:` | yes | no | no | no | rar |
| `zip:` | yes | no | no | no | zip |
| `zip:file:` | yes | no | no | no | zip |
| `zip:jar:` | yes | no | no | no | zip |
| `zip:nested:` | yes | no | no | no | zip |
| `zip:url:` | yes | no | no | no | zip |
| `tar:` | yes | no | no | no | tar |
| `tar:file:` | yes | no | no | no | tar |
| `tar:jar:` | yes | no | no | no | tar |
| `tar:nested:` | yes | no | no | no | tar |
| `tar:url:` | yes | no | no | no | tar |
| `tgz:` | yes | no | no | no | tgz |
| `tgz:file:` | yes | no | no | no | tgz |
| `tgz:jar:` | yes | no | no | no | tgz |
| `tgz:nested:` | yes | no | no | no | tgz |
| `tgz:url:` | yes | no | no | no | tgz |
| `tbz:` | yes | no | no | no | tbz |
| `tbz:file:` | yes | no | no | no | tbz |
| `tbz:jar:` | yes | no | no | no | tbz |
| `tbz:nested:` | yes | no | no | no | tbz |
| `tbz:url:` | yes | no | no | no | tbz |
| `tbz2:` | yes | no | no | no | tbz2 |
| `tbz2:file:` | yes | no | no | no | tbz2 |
| `tbz2:jar:` | yes | no | no | no | tbz2 |
| `tbz2:nested:` | yes | no | no | no | tbz2 |
| `tbz2:url:` | yes | no | no | no | tbz2 |
| `txz:` | yes | no | no | no | txz |
| `txz:file:` | yes | no | no | no | txz |
| `txz:jar:` | yes | no | no | no | txz |
| `txz:nested:` | yes | no | no | no | txz |
| `txz:url:` | yes | no | no | no | txz |
| `tzst:` | yes | no | no | no | tzst |
| `tzst:file:` | yes | no | no | no | tzst |
| `tzst:jar:` | yes | no | no | no | tzst |
| `tzst:nested:` | yes | no | no | no | tzst |
| `tzst:url:` | yes | no | no | no | tzst |
| `tar:gz:` | yes | no | no | no | tar.gz |
| `tar:bz2:` | yes | no | no | no | tar.bz2 |
| `tar:xz:` | yes | no | no | no | tar.xz |
| `tar:zst:` | yes | no | no | no | tar.zst |
| `tar:lz4:` | yes | no | no | no | tar.lz4 |
| `tar:lzma:` | yes | no | no | no | tar.lzma |
| `tar:lzip:` | yes | no | no | no | tar.lzip |
| `tar:lzop:` | yes | no | no | no | tar.lzop |
| `tar:compress:` | yes | no | no | no | tar.compress |
| `tar:z:` | yes | no | no | no | tar.z |
| `tar:Z:` | yes | no | no | no | tar.Z |
| `tar:pack:` | yes | no | no | no | tar.pack |
| `tar:jar:` | yes | no | no | no | tar.jar |
| `tar:war:` | yes | no | no | no | tar.war |
| `tar:ear:` | yes | no | no | no | tar.ear |
| `tar:sar:` | yes | no | no | no | tar.sar |
| `tar:rar:` | yes | no | no | no | tar.rar |
| `tar:zip:` | yes | no | no | no | tar.zip |
| `tar:tar:` | yes | no | no | no | tar.tar |
| `tar:tgz:` | yes | no | no | no | tar.tgz |
| `tar:tbz:` | yes | no | no | no | tar.tbz |
| `tar:tbz2:` | yes | no | no | no | tar.tbz2 |
| `tar:txz:` | yes | no | no | no | tar.txz |
| `tar:tzst:` | yes | no | no | no | tar.tzst |
| `tar:gz:` | yes | no | no | no | tar.gz |
| `tar:bz2:` | yes | no | no | no | tar.bz2 |
| `tar:xz:` | yes | no | no | no | tar.xz |
| `tar:zst:` | yes | no | no | no | tar.zst |
| `tar:lz4:` | yes | no | no | no | tar.lz4 |
| `tar:lzma:` | yes | no | no | no | tar.lzma |
| `tar:lzip:` | yes | no | no | no | tar.lzip |
| `tar:lzop:` | yes | no | no | no | tar.lzop |
| `tar:compress:` | yes | no | no | no | tar.compress |
| `tar:z:` | yes | no | no | no | tar.z |
| `tar:Z:` | yes | no | no | no | tar.Z |
| `tar:pack:` | yes | no | no | no | tar.pack |
| `tar:jar:` | yes | no | no | no | tar.jar |
| `tar:war:` | yes | no | no | no | tar.war |
| `tar:ear:` | yes | no | no | no | tar.ear |
| `tar:sar:` | yes | no | no | no | tar.sar |
| `tar:rar:` | yes | no | no | no | tar.rar |
| `tar:zip:` | yes | no | no | no | tar.zip |
| `tar:tar:` | yes | no | no | no | tar.tar |
| `tar:tgz:` | yes | no | no | no | tar.tgz |
| `tar:tbz:` | yes | no | no | no | tar.tbz |
| `tar:tbz2:` | yes | no | no | no | tar.tbz2 |
| `tar:txz:` | yes | no | no | no | tar.txz |
| `tar:tzst:` | yes | no | no | no | tar.tzst |

The rows repeat by construction — the matrix is a *scheme-surface
map*, not a taxonomy — the nested-compress/pack200/ear-rar-war-zip
tail is included for completeness because Java URL handlers accept
compound schemes.
