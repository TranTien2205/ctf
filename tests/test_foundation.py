import contextlib
import io
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
from email.message import Message

import ctf
from tools import plan, promote_card, run, state, validate_card, web_probe, writeup_search
from tools import benchmark

ROOT = Path(__file__).resolve().parents[1]


class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def cli(self, *args):
        return subprocess.run([sys.executable, *map(str, args)], cwd=ROOT,
                              capture_output=True, text=True, timeout=10)

    def state_call(self, *args):
        with patch.object(state, "ROOT", str(self.root)), patch.object(sys, "argv", ["state", *args]), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            state.main()

    def test_routes_boundaries_and_skills(self):
        for text in ("myself", "workshop", "crop", "hashbrown", "rsaish", "httpish"):
            self.assertIsNone(ctf.observation_route(text)["route"], text)
        for text, category in (("rev", "rev"), ("disassembly", "rev"), ("SQL injection", "web"), ("steganography", "forensics")):
            route = ctf.observation_route(text)["route"]
            self.assertEqual(route["category"], category)
            self.assertTrue((ROOT / route["skill"]).is_file())
        routed = ctf.observation_route("Next.js login cookie")
        self.assertEqual(routed["route"]["score"], 3)
        self.assertNotIn("web", [r["category"] for r in routed["alternates"]])

    def test_sql_fstring_source(self):
        path = self.root / "example.py"
        path.write_text('db.execute(f"SELECT * FROM users WHERE name = {name}")')
        self.assertIn("SQL injection", [f["signal"] for f in ctf.source_route(str(path))["findings"]])
        path.write_text('db.execute("SELECT * FROM users WHERE name = ?", (name,))')
        self.assertNotIn("SQL injection", [f["signal"] for f in ctf.source_route(str(path))["findings"]])

    def test_fts_literals_and_errors(self):
        knowledge = self.root / "knowledge"
        knowledge.mkdir()
        database = knowledge / "ctf.sqlite3"
        with contextlib.closing(sqlite3.connect(database)) as db:
            with db:
                db.execute("CREATE VIRTUAL TABLE cards USING fts5(id,name,event,category,technique,signals,first_probe,source_url)")
                db.execute("INSERT INTO cards VALUES (?,?,?,?,?,?,?,?)", ("abc", "server-side fetch", "event", "web", "ssrf", "fetch", "baseline", "https://example.org"))
        with patch.object(ctf, "ROOT", str(self.root)):
            self.assertEqual(len(ctf.related_cards('server-side OR " fetch:')), 1)
        proc = self.cli(ROOT / "tools/query_index.py", 'server-side OR " fetch:', "--db", database, "--json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(len(json.loads(proc.stdout)["results"]), 1)
        missing = self.root / "absent.db"
        proc = self.cli(ROOT / "tools/query_index.py", "test", "--db", missing)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("error", json.loads(proc.stdout))
        self.assertFalse(missing.exists())
        database.write_bytes(b"not sqlite")
        with patch.object(ctf, "ROOT", str(self.root)):
            self.assertEqual(ctf.related_cards("fetch"), [])

    def test_planner_registry_and_ranking(self):
        for observation, technique in (("JWT login", "jwt"), ("RSA modulus", "rsa"), ("rev disassembly", "validation-path"), ("login SQL database query URL", "sqli")):
            with patch.object(sys, "argv", ["plan", observation, "--json"]), contextlib.redirect_stdout(io.StringIO()) as out:
                plan.main()
            result = json.loads(out.getvalue())
            self.assertEqual(result["mode"], "first-probe-plan")
            self.assertIn(technique, [h["technique"] for h in result["hypotheses"]])
            self.assertEqual(result["hypotheses"], sorted(result["hypotheses"], key=lambda h: -h["score"]))
            if technique == "rsa":
                self.assertEqual(result["hypotheses"][0]["probe"], "collect n/e/c and key size")

    def test_http_error_evidence(self):
        headers = Message()
        headers["Content-Type"] = "text/html"
        headers["X-Powered-By"] = "Next.js"
        body = b'<form action="/login"><input name="token"></form>'
        error = urllib.error.HTTPError("https://example.invalid/login", 403, "Forbidden", headers, io.BytesIO(body))
        with patch.object(web_probe.urllib.request, "urlopen", side_effect=error):
            result = web_probe.probe("https://example.invalid", 1)
        self.assertEqual(result["status"], 403)
        self.assertEqual(result["length_sample"], len(body))
        self.assertEqual(result["forms"][0]["action"], "/login")
        self.assertIn("nextjs", result["signals"])
        self.assertEqual(result["headers"]["X-Powered-By"], "Next.js")
        self.assertEqual(result["final_url"], "https://example.invalid/login")
        response = urllib.error.HTTPError("https://example.invalid", 200, "OK", headers, io.BytesIO(body))
        with patch.object(web_probe.urllib.request, "urlopen", return_value=response):
            success = web_probe.probe("https://example.invalid", 1)
        self.assertEqual(success["sha256_sample"], result["sha256_sample"])
        with patch.object(web_probe.urllib.request, "urlopen", side_effect=urllib.error.URLError("offline")):
            self.assertEqual(web_probe.probe("https://example.invalid", 1)["result"], "error")

    def test_state_safe_ids(self):
        with patch.object(state, "ROOT", str(self.root)):
            for name in ("", ".", "..", "../escape", "/tmp/escape", "two words", "x" * 101):
                with self.assertRaises(ValueError):
                    state.path_for(name)
            self.assertEqual(Path(state.path_for("Offlinea")).parent.name, "offlinea")
            (self.root / "challenges").mkdir()
            (self.root / "challenges/linked").symlink_to(self.root, target_is_directory=True)
            with self.assertRaises(ValueError):
                state.path_for("linked")

    def test_state_preservation_and_selective_lifecycle(self):
        self.state_call("sample", "--hypothesis", "first")
        self.state_call("sample", "--hypothesis", "second")
        path = self.root / "challenges/sample/state.json"
        data = json.loads(path.read_text())
        data["custom"] = {"keep": True}
        del data["hypotheses"][1]["id"]  # Existing states shipped without IDs.
        path.write_text(json.dumps(data))
        first = data["hypotheses"][0]["id"]
        self.assertEqual(data["hypotheses"][0]["priority"], 50)
        self.state_call("sample", "--hypothesis-id", first, "--close", "falsified", "--probe", "baseline")
        updated = json.loads(path.read_text())
        self.assertEqual(updated["custom"], data["custom"])
        self.assertEqual([h["status"] for h in updated["hypotheses"]], ["closed", "open"])
        self.assertIn("id", updated["hypotheses"][1])
        self.assertEqual(updated["probes"][-1]["hypothesis_id"], first)
        before = path.read_bytes()
        with self.assertRaises(SystemExit):
            self.state_call("sample", "--close", "all")
        self.assertEqual(path.read_bytes(), before)
        for invalid in (b"{broken", b"[]", b'{"hypotheses":null,"probes":[]}'):
            path.write_bytes(invalid)
            with self.assertRaises(SystemExit):
                self.state_call("sample", "--hypothesis", "lost")
        self.assertEqual(path.read_bytes(), invalid)

    def test_state_priority_is_explicit(self):
        self.state_call("sample", "--hypothesis", "old")
        path = self.root / "challenges/sample/state.json"
        data = json.loads(path.read_text())
        hid = data["hypotheses"][0]["id"]
        self.state_call("sample", "--hypothesis-id", hid, "--deprioritize", "no new signal")
        updated = json.loads(path.read_text())
        self.assertEqual(updated["hypotheses"][0]["priority"], 0)
        self.assertEqual(updated["hypotheses"][0]["status"], "open")

    def test_atomic_failure_preserves_original(self):
        path = self.root / "state.json"
        path.write_text('{"original": true}')
        with patch.object(state.os, "replace", side_effect=OSError("simulated")):
            with self.assertRaises(OSError):
                state.atomic_json(str(path), {"replacement": True})
        self.assertEqual(json.loads(path.read_text()), {"original": True})
        self.assertEqual(list(self.root.iterdir()), [path])

    def card(self):
        return {"schema_version": 1, "id": "test-card", "challenge": {"name": "Test", "category": "web"},
                "classification": {"primary": "sqli", "confidence": 0.8},
                "source": {"url": "https://example.org/writeup", "retrieved_at": "2026-09-05", "evidence_spans": ["sample"]},
                "quality": {"verified_live": False, "review_status": "extracted"}}

    def test_card_schema_and_malformed_shapes(self):
        self.assertEqual(validate_card.validate(self.card()), [])
        for value in (None, [], "string", 7):
            self.assertTrue(validate_card.validate(value))
        mutations = (("schema_version", 2), ("id", "../escape"), ("id", "abc\n"), ("challenge", []),
                     ("classification", {"primary": "x", "confidence": 2}), ("signals", [1]),
                     ("source", {"url": "not a uri", "retrieved_at": "today", "evidence_spans": [1]}),
                     ("quality", {"verified_live": True, "review_status": "reviewed"}))
        for key, value in mutations:
            card = self.card()
            card[key] = value
            self.assertTrue(validate_card.validate(card), (key, value))
        for section, key in (("classification", "confidence"), ("source", "retrieved_at"), ("quality", "verified_live")):
            card = self.card()
            del card[section][key]
            self.assertTrue(validate_card.validate(card))
        card = self.card()
        card["classification"]["confidence"] = float("nan")
        self.assertTrue(validate_card.validate(card))

    def test_promotion_containment_and_no_overwrite(self):
        with patch.object(promote_card, "ROOT", self.root):
            destination = Path(promote_card.promote(self.card(), {"accept": True}, self.root / "cards"))
            before = destination.read_bytes()
            with self.assertRaises(FileExistsError):
                promote_card.promote(self.card(), {"accept": True}, self.root / "cards")
            self.assertEqual(destination.read_bytes(), before)
            with self.assertRaises(ValueError):
                promote_card.promote(self.card(), {"accept": True}, ROOT)
            with self.assertRaises(ValueError):
                promote_card.promote(self.card(), {"accept": False}, self.root / "cards")
            (self.root / "outside").symlink_to(ROOT, target_is_directory=True)
            with self.assertRaises(ValueError):
                promote_card.promote(self.card(), {"accept": True}, self.root / "outside")

    def test_run_recording_and_timeout(self):
        with patch.object(state, "ROOT", str(self.root)), patch.object(run, "ROOT", str(self.root)):
            argv = [sys.executable, "-c", "import sys; print(sys.argv[1]); print('err', file=sys.stderr); sys.exit(3)", "literal; $(not-a-command)"]
            metadata, result = run.record("sample", argv, self.root, 5)
            directory = Path(metadata).parent
            self.assertEqual(result["returncode"], 3)
            self.assertEqual((directory / "stdout.bin").read_text().strip(), argv[-1])
            self.assertEqual((directory / "stderr.bin").read_text().strip(), "err")
            self.assertEqual(json.loads(Path(metadata).read_text())["argv"], argv)
            _, result = run.record("sample", [sys.executable, "-c", "import time; time.sleep(5)"], self.root, 0.05)
            self.assertEqual(result["status"], "timeout")
            _, result = run.record("sample", [str(self.root / "nonexistent")], self.root, 1)
            self.assertEqual(result["status"], "error")
            with self.assertRaises(ValueError):
                run.record("sample", argv, ROOT, 1)

    def test_run_cli_argument_parsing(self):
        # Parse the actual CLI without creating persistent challenge records.
        result = {"status": "completed", "returncode": 0}
        with patch.object(sys, "argv", ["run", "--timeout", "2", "--cwd", str(ROOT), "example", "--", sys.executable, "-c", "print('ok')"]), patch.object(run, "record", return_value=("run.json", result)) as record, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run.main(), 0)
        record.assert_called_once_with("example", [sys.executable, "-c", "print('ok')"], str(ROOT), 2.0)

    def test_benchmark_verifies_and_rejects(self):
        result = benchmark.run(timeout=5)
        self.assertEqual(result["status"], "verified")
        self.assertTrue(result["verification"])
        result = benchmark.run(timeout=5, wrong=True)
        self.assertEqual(result["status"], "failed")
        self.assertFalse(result["verification"])


class WriteupSearchTests(unittest.TestCase):
    def test_ddg_parses_results_and_uddg_targets(self):
        html = ('<a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fw"'
                '>Title <b>x</b></a>')
        with patch.object(writeup_search, "get", return_value=html):
            rows = writeup_search.ddg("query")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["url"], "https://example.com/w")
        self.assertEqual(rows[0]["title"], "Title x")
        self.assertEqual(rows[0]["source"], "duckduckgo")

    def test_ddg_anomaly_page_raises_instead_of_silent_empty(self):
        with patch.object(writeup_search, "get", return_value="challenge-form anomaly.js ..."):
            with self.assertRaises(RuntimeError):
                writeup_search.ddg("query")

    def test_github_queries_name_description_readme(self):
        captured = {}

        def fake_get(url, timeout=10, headers=None):
            captured["url"] = url
            return json.dumps({"items": []})

        with patch.object(writeup_search, "get", fake_get):
            writeup_search.github("TornadoService")
        self.assertIn("in%3Aname%2Cdescription%2Creadme", captured["url"])


if __name__ == "__main__":
    unittest.main()
