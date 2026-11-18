# Java Sinks — Runtime.exec, ProcessBuilder, ScriptEngine

## The sink table

| Call | Shell? | Notes |
|---|---|---|
| `Runtime.exec(String)` | special tokenize | see below — NOT sh -c! |
| `Runtime.exec(String[])` | NO shell | argv |
| `new ProcessBuilder(String...)` | NO shell | argv list |
| `new ProcessBuilder("sh","-c",cmd)` | sh -c | explicit shell |
| `ScriptEngine.eval(code)` | JS/other eval | Nashorn/Groovy eval — exec via engine |
| `GroovyShell.evaluate` | groovy eval | groovy code → shell |
| `ScriptEngineManager.getEngineByName` | engine eval | spel/js/groovy/mvel |
| `Class.forName(...).newInstance` | class load | reflection exec |
| `javax.el`/`SpEL` expression eval | expression eval | `eval-injection.md` |
| `JdbcRowSet`/JNDI lookups | deser | `web-deserialization/jndi-injection` |
| `ProcessBuilder.start` redirect | file write | redirects |

## `Runtime.exec(String)` — the tokenizer trap

```java
Runtime.getRuntime().exec("ping " + host)
```

The String form tokenizes on whitespace — `host="127.0.0.1;id"` →
tokens `ping`,`127.0.0.1;id` — the `;` is INSIDE token 2 — passed to
`ping` as argv — `ping` fails on the weird host but NO shell runs.

**`Runtime.exec(String)` does NOT invoke a shell** — the metachar
injection fails. Escape routes:

- `Runtime.exec(new String[]{"sh","-c","ping "+host})` — explicit sh -c
- if the string contains a space-injection: `host="x -y"` — tokenization
  splits YOUR spaces — argument-splitting injection! `host` carrying
  `x -c` — `-c` lands as ping's flag → `argument-injection.md`
- `Runtime.exec` on Windows → `cmd /c`? No — exec(String) on Windows
  tokenizes differently but still no cmd.exe unless explicit.

So `Runtime.exec(str)` → space-split argv, no shell. The INJECTION
VECTOR is spaces splitting your input into multiple args — flag
injection via whitespace.

## `ProcessBuilder` — argv only

```java
new ProcessBuilder("ping", host).start()
new ProcessBuilder("sh","-c","ping "+host).start()
```

Second form is the bug — the `sh -c` string is where injection lives.

## `ProcessBuilder` with a LIST — the shell-mode signal

`new ProcessBuilder("bash","-c",cmd)` — `cmd` is your injection — full
bash syntax.

## `ScriptEngine` — Nashorn/Groovy eval

```java
ScriptEngineManager().getEngineByName("js").eval(code)
new GroovyShell().evaluate(code)
```

JS (Nashorn <JDK15)/Groovy eval — code exec — `eval-injection.md` —
`Runtime.getRuntime().exec("id")` inside JS-engine code reaches a shell.

## SpEL/OGNL/MVEL/JEXL — expression languages

`spel.eval(...)`, `OGNL.getValue`, `MVEL.eval` — expression evaluators —
the classic EL-injection (`T(java.lang.Runtime).getRuntime().exec()`)
— `eval-injection.md` — same class per chain-card widening.

## `ProcessBuilder.environment()` — env control

If `environment().put(k, v)` is user-fed — `PATH`/`LD_PRELOAD` —
`env-var-injection.md`.

## `loadClass`/`defineClass` — bytecode loading

`Class.forName(userClass)`/`defineClass(byte[])` — upload a class/jar
then load — `jar-war-deploy`/`web-deserialization` overlap.

## The `Runtime.exec` Windows difference

`exec("cmd /c " + x)` — explicit cmd — the `/c` arg is the shell string
— injectable.

## Detection — which form reached Java

Errors: `java.lang.ProcessBuilder`/`Cannot run program "x;id"` (argv
mode shows the literal `;`), `Cannot run program "sh"` (sh missing),
`IOException: error=2` (ENOENT = argv boundary).

`Cannot run program "x;id": error=2` — the `;` in the error string is
verbatim argv evidence — **argv boundary confirmed, shell absent**.

vs `sh: 1: ...` errors — shell present.

## Falsifiers

- `exec(String)` tokenize confirmed AND no flag-accepting command AND
  no space-splitting (input is single token) — still check for
  `Runtime.exec(String[])`/`ProcessBuilder` elsewhere
- `sh -c` absent AND ScriptEngine/EL not reachable

## Output to record

- sink signature (String vs String[] vs ProcessBuilder(sh,-c)) + the
  exact error string that reveals the boundary
