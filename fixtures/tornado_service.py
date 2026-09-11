#!/usr/bin/env python3
"""Loopback-only benchmark service; not a secure sandbox."""
import argparse
import tornado.ioloop
import tornado.web

class Solve(tornado.web.RequestHandler):
    def post(self):
        if self.request.headers.get("X-Benchmark-Secret") != self.settings["secret"]:
            self.set_status(403); return
        self.write({"flag": self.settings["flag"]})

def main():
    p = argparse.ArgumentParser(); p.add_argument("--port", type=int, required=True); p.add_argument("--secret", required=True); p.add_argument("--flag", required=True)
    a = p.parse_args(); tornado.web.Application([(r"/solve", Solve)], secret=a.secret, flag=a.flag).listen(a.port, "127.0.0.1"); tornado.ioloop.IOLoop.current().start()
if __name__ == "__main__": main()
