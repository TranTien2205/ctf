# Per-Stack File Read — Java / Python / Node / Ruby / Go / .NET

## Java — `new FileInputStream`/`Files.read*`/`getResourceAsStream`

```java
new FileInputStream(path)
Files.readAllBytes(Paths.get(path))
Files.readString(Path.of(path))
new FileReader(path)
BufferedReader(new FileReader(path))
getClass().getResourceAsStream("/" + path)
getServletContext().getResourceAsStream("/" + path)
new File(path).toURI().toURL().openStream()
```

- `getResourceAsStream("/x")` — the classpath resource — `classpath:`-
  relative — reads inside the JAR
- `getServletContext().getResourceAsStream("/WEB-INF/x")` — the webroot
  resource — the `/WEB-INF/` path is the classic Java-LFI
- `new FileInputStream` — the raw file-read
- `Files.read*` — the NIO reads

### The `/WEB-INF/` read — Java's special path

```
?file=/WEB-INF/web.xml
?file=/WEB-INF/applicationContext.xml
?file=/WEB-INF/classes/application.properties
?file=/WEB-INF/classes/config.yml
?file=/WEB-INF/classes/secret.properties
?file=/WEB-INF/lib/app.jar
?file=/WEB-INF/classes/META-INF/persistence.xml
?file=/WEB-INF/classes/logback.xml
?file=/WEB-INF/classes/log4j*.xml
?file=/WEB-INF/weblogic.xml
?file=/WEB-INF/jboss-web.xml
?file=/WEB-INF/struts-config.xml
?file=/WEB-INF/spring*.xml
?file=/WEB-INF/faces-config.xml
?file=/WEB-INF/beans.xml
?file=/WEB-INF/decorators.xml
?file=/WEB-INF/glassfish-web.xml
```

`/WEB-INF/` is Java's config-dir — the resource-read surface.

### `getResourceAsStream` classpath vs file path

`getResourceAsStream("/x")` resolves `x` on the CLASSPATH — inside the
jar/war — `..` doesn't escape the classpath — the "the classpath is
the boundary" quirk — absolute `file:///` paths still work through
`new FileInputStream`.

### `jar:`/`netdoc:` — the archive-URL

```
jar:file:///x.jar!/inside/path
jar:file:///app.war!/WEB-INF/web.xml
netdoc:///etc/passwd
```

`../../web-xxe/references/java-specific.md`/`../../web-ssrf/references/url-parsing.md` territory — reads inside archives.

## Python — `open()`/`os.open`/`pathlib`/`shutil`/`io`/`fileinput`

```python
open(path).read()
open(path, 'rb').read()
os.open(path, os.O_RDONLY)
pathlib.Path(path).read_text()
pathlib.Path(path).read_bytes()
io.open(path).read()
fileinput.input([path])
with open(path) as f: f.read()
```

- `open(path)` — the standard read
- `pathlib.Path(path).read_text()` — the modern read
- `os.popen(path).read()` — NOT a read — a command — different sink
- `os.listdir(path)`/`os.scandir(path)`/`glob.glob(path)` — listing
- `os.path.join(base, path)` — the concat — absolute path replaces
- `os.path.normpath`/`realpath`/`abspath` — normalize
- `shutil.copyfileobj`/`copy` — copy-sinks

### `os.path.join` — the absolute-path quirk

```python
os.path.join("/app", "/etc/passwd")      — returns "/etc/passwd" — absolute wins
os.path.join("/app", "../../etc/passwd") — returns "/app/../../etc/passwd" — resolves out
```

`os.path.join` — absolute second-arg replaces the base — `..` resolves
out — the traversal is always live if `join` is used.

### `send_file`/`send_from_directory`/`FileResponse`/`open`/`tarfile`/`zipfile`

```python
flask.send_file(path)
flask.send_from_directory(dir, path)     — "safely" joins — but traversal may still work
django.http.FileResponse(open(path, 'rb'))
tarfile.open(path)
zipfile.ZipFile(path)
```

`send_from_directory` — Flask's safe-join — historical traversal CVEs —
still testable.

## Node — `fs.readFile*`/`fs.createReadStream`/`require`/`path`/`sendFile`

```javascript
fs.readFileSync(path)
fs.readFile(path, cb)
fs.createReadStream(path)
fs.createWriteStream(path)
path.join(base, path)                    — absolute replaces
path.resolve(path)
require(path)                            — the require — loads + executes!
res.sendFile(path)
res.download(path)
express.static(dir)
```

- `fs.readFileSync`/`readFile` — the read
- `require(path)` — LOADS + EXECUTES — the require-as-RCE — a `.js`
  file require'd runs
- `res.sendFile` — express's safe-join — `root:` option needed
- `path.join`/`resolve` — absolute/`..` handling

### `require` — the exec-sink

```javascript
require("/tmp/evil.js")                  — loads + executes the module
require("/etc/passwd")                   — parses as JS — errors — the error-oracle
require("./config.js")
```

`require` of a `.js` executes it — `require` of a `.json` parses it —
`require` of a `.node` loads a native addon — the require-family is
exec+parse.

### `express.static`/`sendFile` — the static-file surface

`express.static(dir)` + `sendFile` — the static-file handler —
`?file=../../` traversal against the static root — the `root:`-
confine check.

## Ruby — `File.read`/`IO.read`/`open`/`File.open`/`load`/`require`/`send_file`/`render`

```ruby
File.read(path)
File.readlines(path)
File.open(path).read
IO.read(path)
IO.foreach(path)
load(path)                               — loads + executes
require(path)                            — loads + executes
require_relative(path)
send_file(path)
render file: path
File.exist?(path)
File.directory?(path)
Dir.glob(path)
Dir.entries(path)
File.fnmatch(pattern, path)
```

- `File.read`/`IO.read` — the read
- `load`/`require`/`require_relative` — exec
- `render file:`/`send_file` — the framework-read
- `Dir.glob`/`Dir.entries` — listing

## Go — `os.ReadFile`/`ioutil.ReadFile`/`os.Open`/`http.ServeFile`

```go
os.ReadFile(path)
ioutil.ReadFile(path)                    — deprecated
os.Open(path)
http.ServeFile(w, r, path)
http.ServeContent(w, r, name, mtime, reader)
template.ParseFiles(path)
```

Go is type-safe — no `include`-style exec — `http.ServeFile` is the
framework-read — `path.Join`/`filepath.Join` absolute/`..` handling.

### `http.ServeFile`/`ServeContent` — the Go-serve

```go
http.ServeFile(w, r, path)               — serves path — has own traversal-check in some versions
http.ServeFileFS(w, r, fsys, path)
template.ParseFiles(path)                — parses + may exec
```

`ServeFile` has built-in `..`-sanitization in modern Go — the confine
may be live — the `?file=`-param may still reach `os.ReadFile` raw.

## .NET — `File.ReadAll*`/`File.OpenRead`/`FileStream`/`StreamReader`/`MapPath`/`Response.WriteFile`/`VirtualPathProvider`

```csharp
File.ReadAllText(path)
File.ReadAllBytes(path)
File.ReadAllLines(path)
File.OpenRead(path)
new FileStream(path, FileMode.Open)
new StreamReader(path)
Server.MapPath(path)                     — maps to the webroot
Response.WriteFile(path)
Response.TransmitFile(path)
VirtualPathProvider.GetFile(path)
HostingEnvironment.MapPath(path)
Assembly.LoadFrom(path)                  — LOADS + execs a .dll!
```

- `File.Read*` — the read family
- `MapPath`/`WriteFile`/`TransmitFile` — the framework-read
- `Assembly.LoadFrom(path)` — loads a .NET assembly — exec — the
  .NET exec-sink
- `VirtualPathProvider` — the virtualized-fs — `~/` paths

## The "the sink names the primitive" — the per-stack boundary

| Stack | Read | Exec |
|---|---|---|
| PHP | `file_get_contents`/`readfile`/`file`/`fpassthru` | `include`/`require`/`eval` |
| Python | `open`/`Path.read`/`send_file`/`FileResponse` | `exec`/`eval`/`__import__`/`importlib`/`subprocess` |
| Node | `fs.readFile`/`createReadStream`/`sendFile` | `require`/`eval`/`exec`/`spawn`/`fork`/`import()` |
| Ruby | `File.read`/`IO.read`/`send_file` | `load`/`require`/`eval`/`system`/`exec`/`spawn` |
| Java | `FileInputStream`/`Files.read*`/`getResourceAsStream` | `Runtime.exec`/`ProcessBuilder`/`ScriptEngine.eval`/`loadClass` |
| .NET | `File.Read*`/`StreamReader`/`WriteFile` | `Assembly.Load*`/`Process.Start`/`eval` |
| Go | `os.ReadFile`/`os.Open`/`ServeFile` | `exec.Command`/`plugin.Open`/`template.ParseFiles` |
