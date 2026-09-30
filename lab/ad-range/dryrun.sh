#!/bin/sh
# Timed rehearsal for the attack-defense control plane. Run it the night before.
#
# Its purpose is NOT to teach. It is to find the config field nobody filled in,
# the flag regex that does not match, and the submit dialect that is wrong -- while
# there is still time. Four paths are otherwise untested until the contest itself:
#
#   1. the SLA bracket, including a real regression AND a deleted check
#   2. the farm's HELD-flag path: scoreboard down, then up, then the ALERT
#   3. capture -> cap_split -> traffic_mine, offline
#   4. tick.py's answer at each state
#
# No network, no docker, no sudo. Two stdlib HTTP servers on 19080 and 19081.
# Port 18080 is deliberately NOT used: it was measured taken on this box.
#
#   sh lab/ad-range/dryrun.sh
#
# Exit 0 only when every path passes. Every process and temporary directory is
# removed on success and on failure, because a capture or a server left running
# after a rehearsal is how the real contest starts with a port already bound.
set -u

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
PY=python3
SVC_PORT=19080
BOARD_PORT=19081
WORK=$(mktemp -d)
PASS=0
FAIL=0
SVC_PID=""
BOARD_PID=""

cleanup() {
    [ -n "$SVC_PID" ] && kill "$SVC_PID" 2>/dev/null
    [ -n "$BOARD_PID" ] && kill "$BOARD_PID" 2>/dev/null
    wait 2>/dev/null
    rm -rf "$WORK"
}
trap cleanup EXIT HUP INT TERM

say()  { printf '%s\n' "$*"; }
ok()   { PASS=$((PASS+1)); printf '  PASS  %s\n' "$*"; }
bad()  { FAIL=$((FAIL+1)); printf '  FAIL  %s\n' "$*"; }
skip() { printf '  SKIP  %s\n' "$*"; }

say "=== attack-defense dry run ==="
say "root      $ROOT"
say "workdir   $WORK"
say ""

# ---------------------------------------------------------------- the service
mkdir -p "$WORK/www"
printf 'notes service\n' > "$WORK/www/index.html"
printf 'stored\n' > "$WORK/www/note"
( cd "$WORK/www" && exec "$PY" -m http.server "$SVC_PORT" --bind 127.0.0.1 ) \
    >"$WORK/svc.log" 2>&1 &
SVC_PID=$!

# a scoreboard that accepts a PUT and says so
cat > "$WORK/board.py" <<'PYEOF'
import http.server, socketserver, sys
class H(http.server.BaseHTTPRequestHandler):
    def do_PUT(self):
        n = int(self.headers.get("Content-Length") or 0)
        self.rfile.read(n)
        self.send_response(200); self.end_headers(); self.wfile.write(b"accepted")
    do_POST = do_PUT
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
socketserver.TCPServer(("127.0.0.1", int(sys.argv[1])), H).serve_forever()
PYEOF

# wait for the service, rather than sleeping and hoping
i=0
while [ "$i" -lt 40 ]; do
    if "$PY" - "$SVC_PORT" <<'PYEOF' 2>/dev/null
import socket, sys
s = socket.socket(); s.settimeout(0.25)
sys.exit(0 if s.connect_ex(("127.0.0.1", int(sys.argv[1]))) == 0 else 1)
PYEOF
    then break; fi
    i=$((i+1))
done
if [ "$i" -ge 40 ]; then
    say "the rehearsal service never came up on $SVC_PORT; nothing below can run"
    exit 1
fi

# ------------------------------------------------------- 1. the SLA bracket
say "1. the SLA bracket"
cat > "$WORK/spec.json" <<PYEOF
{"service": "notes", "base": "http://127.0.0.1:$SVC_PORT",
 "checks": [{"name": "index", "path": "/", "expect_status": 200},
            {"name": "store_note", "path": "/note", "expect_status": 200,
             "expect_contains": "stored"}]}
PYEOF

"$PY" "$ROOT/tools/ad/sla_check.py" "$WORK/spec.json" --save "$WORK/before.json" >/dev/null 2>&1
if [ $? -eq 0 ]; then ok "a green baseline saves and exits 0"
else bad "the baseline is not green -- fix that before trusting anything below"; fi

# a REAL regression: the feature the checker exercises is removed
rm -f "$WORK/www/note"
"$PY" "$ROOT/tools/ad/sla_check.py" "$WORK/spec.json" --save "$WORK/after.json" \
      --compare "$WORK/before.json" >"$WORK/cmp.json" 2>&1
if [ $? -eq 1 ]; then ok "a broken feature exits 1 (REVERT THE PATCH)"
else bad "a broken feature did NOT exit 1 -- the bracket is not protecting you"; fi
printf 'stored\n' > "$WORK/www/note"

# the failure the tool exists to stop: delete the check that noticed
"$PY" - "$WORK/spec.json" "$WORK/spec-trimmed.json" <<'PYEOF'
import json, sys
spec = json.load(open(sys.argv[1]))
spec["checks"] = [c for c in spec["checks"] if c["name"] != "store_note"]
json.dump(spec, open(sys.argv[2], "w"))
PYEOF
"$PY" "$ROOT/tools/ad/sla_check.py" "$WORK/spec-trimmed.json" --save "$WORK/trim.json" \
      --compare "$WORK/before.json" >"$WORK/cmp2.json" 2>&1
if [ $? -eq 1 ]; then ok "DELETING the check is caught too, not blessed"
else bad "a deleted check was blessed -- patch-by-deleting-the-feature is open"; fi

# an unusable spec must be distinguishable from a regression
printf 'not json' > "$WORK/bad.json"
"$PY" "$ROOT/tools/ad/sla_check.py" "$WORK/bad.json" >/dev/null 2>&1
if [ $? -eq 3 ]; then ok "an unusable spec exits 3, not 1"
else bad "an unusable spec is indistinguishable from a regression"; fi
say ""

# ------------------------------------------------------- 2. the held-flag path
say "2. the farm holds flags when the scoreboard is down"
cat > "$WORK/farm.json" <<PYEOF
{"authorized_event": "local dry run", "service": "notes",
 "teams": [{"id": 1, "host": "127.0.0.1"}],
 "exploit": ["printf", "FLAG1\\n"],
 "flag_regex": "FLAG[0-9]",
 "submit": {"url": "http://127.0.0.1:1/flags", "timeout": 2},
 "skip_self": 9}
PYEOF

held=0
alert=0
for tick in 1 2 3; do
    "$PY" "$ROOT/tools/ad/flag_farm.py" "$WORK/farm.json" --once >"$WORK/farm$tick.json" 2>&1
    p=$("$PY" - "$WORK/farm$tick.json" <<'PYEOF'
import json, sys
line = [l for l in open(sys.argv[1]) if l.strip().startswith("{")][-1]
d = json.loads(line)
print("%s %s" % (d.get("pending_flags"), 1 if "ALERT" in d else 0))
PYEOF
)
    held=$(printf '%s' "$p" | cut -d' ' -f1)
    alert=$(printf '%s' "$p" | cut -d' ' -f2)
done
if [ "$held" = "1" ]; then ok "the flag is still HELD after three failed ticks, not lost"
else bad "the flag was discarded when the scoreboard was unreachable (pending=$held)"; fi
if [ "$alert" = "1" ]; then ok "three consecutive failures raise ALERT"
else bad "three consecutive failures raised no ALERT -- an outage would stay silent"; fi

# now the scoreboard comes back and the held flag must drain
"$PY" "$WORK/board.py" "$BOARD_PORT" >/dev/null 2>&1 &
BOARD_PID=$!
i=0
while [ "$i" -lt 40 ]; do
    if "$PY" - "$BOARD_PORT" <<'PYEOF' 2>/dev/null
import socket, sys
s = socket.socket(); s.settimeout(0.25)
sys.exit(0 if s.connect_ex(("127.0.0.1", int(sys.argv[1]))) == 0 else 1)
PYEOF
    then break; fi
    i=$((i+1))
done
"$PY" - "$WORK/farm.json" "$WORK/farm-up.json" "$BOARD_PORT" <<'PYEOF'
import json, shutil, sys
cfg = json.load(open(sys.argv[1]))
cfg["submit"]["url"] = "http://127.0.0.1:%s/flags" % sys.argv[3]
json.dump(cfg, open(sys.argv[2], "w"))
for ext in ("seen", "pending", "fails"):
    try: shutil.copy(sys.argv[1][:-5] + "." + ext, sys.argv[2][:-5] + "." + ext)
    except OSError: pass
PYEOF
"$PY" "$ROOT/tools/ad/flag_farm.py" "$WORK/farm-up.json" --once >"$WORK/farm-up.out" 2>&1
drained=$("$PY" - "$WORK/farm-up.out" <<'PYEOF'
import json, sys
line = [l for l in open(sys.argv[1]) if l.strip().startswith("{")][-1]
d = json.loads(line)
print("%s %s" % (d.get("pending_flags"), d.get("submitted_total")))
PYEOF
)
if [ "$drained" = "0 1" ]; then ok "the held flag drains once the scoreboard answers"
else bad "the held flag did not drain (pending/submitted = $drained)"; fi

# the two guards, since a config typo is the likeliest way to lose the attack score
"$PY" - "$WORK/guard.json" <<'PYEOF'
import json
json.dump({"authorized_event": "x", "teams": [{"id": 1, "host": "10.60.1.*"}],
           "exploit": ["true"], "flag_regex": r"FLAG\{(.*?)\}"},
          open("/dev/stdin".replace("/dev/stdin", __import__("sys").argv[1]), "w"))
PYEOF
"$PY" "$ROOT/tools/ad/flag_farm.py" "$WORK/guard.json" --once >"$WORK/guard.out" 2>&1
if [ $? -ne 0 ] && grep -q 'discovery' "$WORK/guard.out" && grep -q 'capturing group' "$WORK/guard.out"; then
    ok "a wildcard host AND a capturing flag_regex are both refused, in one run"
else
    bad "the config guards did not both fire -- check $WORK/guard.out"
fi
say ""

# ------------------------------------------- 3. capture -> split -> mine
say "3. the capture pipeline, offline"
if [ -f "$ROOT/tools/ad/fixtures/http_requests.fields" ]; then
    "$PY" "$ROOT/tools/ad/cap_split.py" \
        --from-fields "$ROOT/tools/ad/fixtures/http_requests.fields" \
        --out "$WORK/live" >"$WORK/split.json" 2>&1
    n=$("$PY" -c "import json,sys;print(json.load(open(sys.argv[1])).get('requests',0))" "$WORK/split.json" 2>/dev/null)
    if [ "${n:-0}" -gt 0 ]; then ok "cap_split rebuilt $n request(s) with no tshark"
    else bad "cap_split rebuilt nothing -- see $WORK/split.json"; fi

    "$PY" "$ROOT/tools/ad/traffic_mine.py" --live "$WORK/live" --top 5 >"$WORK/mined.json" 2>&1
    c=$("$PY" -c "import json,sys;print(json.load(open(sys.argv[1])).get('candidates',0))" "$WORK/mined.json" 2>/dev/null)
    if [ "${c:-0}" -gt 0 ]; then ok "traffic_mine ranked $c candidate(s)"
    else bad "traffic_mine ranked nothing -- see $WORK/mined.json"; fi

    if grep -q 'HTTP/1.0' "$WORK/mined.json"; then
        bad "the mined output carries RESPONSE bytes -- a replay would aim your own response at a third team"
    else
        ok "no response bytes reached the mined output"
    fi
else
    skip "tools/ad/fixtures/http_requests.fields is absent, so the offline pipeline cannot run"
fi
say ""

# ------------------------------------------------------- 4. the tick decider
say "4. the tick decider"
if [ -f "$ROOT/tools/ad/tick.py" ]; then
    "$PY" "$ROOT/tools/ad/tick.py" "$WORK/ledger.json" --init notes >/dev/null 2>&1
    a=$("$PY" "$ROOT/tools/ad/tick.py" "$WORK/ledger.json" 2>/dev/null \
        | "$PY" -c "import json,sys;print(json.load(sys.stdin).get('action'))" 2>/dev/null)
    if [ "$a" = "intake_step" ]; then ok "a fresh ledger asks for the intake, not an exploit"
    else bad "a fresh ledger answered '$a'"; fi

    # walk the intake, then check the steady-state ordering
    for step in snapshot-before-touching evidence-copied-off-box sla-spec-written-and-green \
                credentials-rotated unknown-keys-and-accounts-removed \
                planted-persistence-swept baseline-capture-started farm-dry-run-proven; do
        "$PY" "$ROOT/tools/ad/tick.py" "$WORK/ledger.json" record --kind intake \
              --field "step=$step" >/dev/null 2>&1
    done
    a=$("$PY" "$ROOT/tools/ad/tick.py" "$WORK/ledger.json" 2>/dev/null \
        | "$PY" -c "import json,sys;print(json.load(sys.stdin).get('action'))" 2>/dev/null)
    if [ "$a" = "close_intake" ]; then ok "a finished intake asks to close the phase"
    else bad "a finished intake answered '$a'"; fi

    "$PY" "$ROOT/tools/ad/tick.py" "$WORK/ledger.json" record --kind phase \
          --field phase=steady >/dev/null 2>&1
    a=$("$PY" "$ROOT/tools/ad/tick.py" "$WORK/ledger.json" 2>/dev/null \
        | "$PY" -c "import json,sys;print(json.load(sys.stdin).get('action'))" 2>/dev/null)
    if [ "$a" = "restore_service" ]; then
        ok "an UNMEASURED service outranks every attack action"
    else
        bad "an unmeasured service answered '$a' -- availability is not first"
    fi
else
    skip "tools/ad/tick.py is absent, so the decider cannot be rehearsed"
fi
say ""

say "=== $PASS passed, $FAIL failed ==="
if [ "$FAIL" -gt 0 ]; then
    say "Fix these tonight. Every one of them is a path that is otherwise first"
    say "exercised during the contest."
    exit 1
fi
say "The plumbing is proven. What this CANNOT prove: the real team host list, the"
say "real flag format, and the real submission dialect. Those come from the brief."
exit 0
