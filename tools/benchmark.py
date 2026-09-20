#!/usr/bin/env python3
"""Reference replay benchmark with exact flag verification."""
import argparse, json, os, secrets, signal, socket, subprocess, sys, time
from urllib.request import Request, urlopen
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def run(timeout=2, wrong=False):
    command=[sys.executable, __file__, "--timeout", str(timeout)]
    if wrong: command.append("--negative")
    result=subprocess.run(command, capture_output=True, text=True, timeout=timeout+3)
    return json.loads(result.stdout)
def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--mode",choices=("reference","unassisted","hint","writeup"),default="reference"); p.add_argument("--timeout",type=float,default=2); p.add_argument("--negative",action="store_true"); a=p.parse_args()
    if a.timeout<=0: p.error("timeout must be positive")
    flag="flag{" + secrets.token_hex(16) + "}"; secret=secrets.token_urlsafe(24); s=socket.socket(); s.bind(("127.0.0.1",0)); port=s.getsockname()[1]; s.close()
    proc=subprocess.Popen([sys.executable,ROOT+"/fixtures/tornado_service.py","--port",str(port),"--secret",secret,"--flag",flag],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True); start=time.monotonic(); status="timeout"; verified=False; error=None
    try:
        while time.monotonic()-start<a.timeout:
            try:
                req=Request("http://127.0.0.1:%d/solve"%port,data=b"",headers={"X-Benchmark-Secret":"wrong" if a.negative else secret},method="POST")
                with urlopen(req,timeout=.2) as r: verified=secrets.compare_digest(json.loads(r.read())["flag"],flag)
                status="verified" if verified else "failed"; break
            except Exception as e:
                error=str(e)
                if a.negative: status="failed"; break
                time.sleep(.01)
    finally:
        os.killpg(proc.pid,signal.SIGTERM)
        try: proc.wait(1)
        except subprocess.TimeoutExpired: os.killpg(proc.pid,signal.SIGKILL); proc.wait()
    print(json.dumps({"mode":"reference replay" if a.mode=="reference" else a.mode,"verification":verified,"wall_seconds":time.monotonic()-start,"status":status,"error":error,"evidence":None},sort_keys=True)); return 0 if (status=="verified") != a.negative else 1
if __name__=="__main__": sys.exit(main())
