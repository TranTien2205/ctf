# Go Sinks — `os/exec`, `syscall`, `net/http` handler surfaces

## The canonical sinks

```go
exec.Command("sh","-c","cmd "+x).Run()          — sh -c — the BUG
exec.Command("cmd", x).Run()                    — argv — SAFE
exec.Command("cmd","arg",x).Run()               — argv — SAFE
exec.Command("sh","-c","cmd "+x).Output()
exec.Command("sh","-c","cmd "+x).CombinedOutput()
exec.CommandContext(ctx,"sh","-c","cmd "+x)
exec.Command("cmd", args...).Run()
exec.Command("bash","-c","cmd "+x)
exec.Command("/bin/sh","-c","cmd "+x)
exec.Command("cmd","/c","cmd "+x).Run()         — windows
syscall.Exec("sh",[]string{"sh","-c","cmd "+x},env)
syscall.Exec("/bin/sh",[]string{"sh","-c",x},os.Environ())
os.StartProcess("/bin/sh",[]string{"sh","-c",x},...)
exec.Cmd{Path:"sh",Args:[]string{"-c","cmd "+x}}
exec.Cmd{Path:"cmd",Args:[]string{"/c","cmd "+x}}
```

## The `exec.Command` signature — the first arg is the BINARY, not a shell

`exec.Command("ping", x)` — `x` is argv[1] — `x="x;id"` is ONE arg —
`ping: x;id: Name or service not known` — no shell — flag-injection
only.

`exec.Command("sh","-c","ping "+x)` — `sh` is the binary, `-c` is the
flag, the string is the shell-line — `;id` splits.

The difference is the FIRST argument — `"sh"`/`"bash"`/`"cmd"`/`"powershell"`
means a shell is invoked; anything else is argv-form.

## The `os.StartProcess`/`syscall.Exec` — exec-replace forms

```go
syscall.Exec("/bin/sh",[]string{"sh","-c",x},os.Environ())  — replaces
syscall.Exec("cmd",[]string{"/c",x},env)                    — cmd /c
os.StartProcess("/bin/sh",[]string{"sh","-c",x},&os.ProcAttr{...})
```

`syscall.Exec` replaces the process — the string still goes through
`sh -c` if `sh` is first.

## The `exec.Cmd` struct form — `Path`/`Args`/`Env`/`Dir`

```go
cmd := exec.Cmd{Path:"sh",Args:[]string{"-c","cmd "+x}}
cmd := exec.Cmd{Path:"ping",Args:[]string{"ping",x}}   — argv
cmd := exec.Cmd{Path:"cmd",Args:[]string{"/c","cmd "+x}}
```

`Args[0]` is conventionally the binary name — `Args[1:]` are args —
`Args` as `[]string{"-c","cmd "+x}` runs the shell-line.

## The net/http handler surfaces — where input reaches exec

```go
http.HandleFunc("/ping",func(w,r){exec.Command("ping",r.FormValue("h")).Output()})
http.HandleFunc("/ping",func(w,r){exec.Command("sh","-c","ping "+r.FormValue("h")).Output()})
http.HandleFunc("/x",func(w,r){exec.Command("sh","-c",r.FormValue("x")).Run()})
```

`r.FormValue`/`r.URL.Query().Get`/`r.PostFormValue`/`r.Header.Get`/
`r.Cookie`/`r.Form`/`r.PostForm`/`mux.Vars`/`r.PathValue`/`chi.URLParam`
— the input points.

## The `gin`/`echo`/`fiber`/`chi`/`mux` framework surfaces

```go
c := gin.Context — c.Query("x")/c.PostForm("x")/c.Param("x")
e := echo.Context — c.QueryParam("x")/c.FormValue("x")/c.Param("x")
f := fiber.Ctx — c.Query("x")/c.Params("x")/c.FormValue("x")
chi.URLParam(r,"x")
mux.Vars(r)["x"]
```

## The `fmt.Sprintf`-concat — where `x` lands

```go
exec.Command("sh","-c",fmt.Sprintf("ping %s",x))
exec.Command("sh","-c","ping "+x)
exec.Command("sh","-c","ping "+strings.Join([]string{x},""))
```

`fmt.Sprintf`/`+`/strings.Join — the concat marker.

## The `exec.LookPath`/`exec.CommandContext` — the binary-path variants

`exec.LookPath("sh")` resolves the binary — the Command still takes
the resolved path — same shell/argv distinction.

## The `text/template`/`html/template` exec — template-eval not cmdi

`template.Must(template.New("x").Parse(x))` — `{{.}}` eval — `web-ssti`.

## The `plugin.Open`/`plugin.Lookup` — Go plugin loading

```go
plugin.Open("/tmp/x.so")      — plugin-load — code-exec
p.Lookup("X")
```

`/tmp/x.so` path control → arbitrary code — but it's .so loading not
cmdi — a different sink.

## The `syscall.Exec`/`os.StartProcess` — fd/env surfaces

`env` — `[]string{"BASH_ENV=/tmp/x"}`/`"LD_PRELOAD=/tmp/x.so"` — env-
injection through the child env — `env-var-injection.md`.

## Falsifiers

- every `exec.Command`/`syscall.Exec` is argv-form (no `sh`/`cmd` first
  arg) AND no eval-reachable path — dead

## Output to record

- the sink-line + whether `sh -c`/`cmd /c`/`shell` was the first arg
