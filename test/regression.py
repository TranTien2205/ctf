#!/usr/bin/env python3
"""Offline regression checks for the CTF solver system."""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import ctf
from tools import state


class SystemRegression(unittest.TestCase):
    def test_all_router_skill_paths_exist(self):
        for path in ctf.SKILLS.values():
            self.assertTrue((ROOT / path).is_file(), path)

    def test_blackbox_and_whitebox_routes(self):
        black = ctf.observation_route("web endpoint fetch admin bot")
        self.assertEqual(black["route"]["category"], "web-ssrf")
        source = ROOT / "challenges/Weather App/web_weather_app/challenge"
        white = ctf.source_route(str(source))
        signals = {item["signal"] for item in white["findings"]}
        self.assertIn("SSRF candidate", signals)
        self.assertIn("SQL injection", signals)
        self.assertTrue(any(item["value"].startswith("HTB{") for item in white["flags"]))

    def test_weather_chain_source_contract(self):
        base = ROOT / "challenges/Weather App/web_weather_app/challenge"
        routes = (base / "routes/index.js").read_text()
        weather = (base / "helpers/WeatherHelper.js").read_text()
        database = (base / "database.js").read_text()
        self.assertRegex(routes, r"/register")
        self.assertIn("remoteAddress", routes)
        self.assertIn("/api/weather", routes)
        self.assertIn("http://${endpoint}", weather)
        self.assertIn("INSERT INTO users", database)
        self.assertIn("ON CONFLICT", (ROOT / "solved/weather_app.md").read_text())

    def test_priority_can_be_lowered_without_deleting_hypothesis(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            root = Path(directory)
            (root / "challenges").mkdir()
            args = ["state", "sample", "--hypothesis", "old path"]
            with patch.object(state, "ROOT", str(root)), patch.object(sys, "argv", args):
                state.main()
            data = json.loads((root / "challenges/sample/state.json").read_text())
            hid = data["hypotheses"][0]["id"]
            args = ["state", "sample", "--hypothesis-id", hid, "--deprioritize", "wrong class"]
            with patch.object(state, "ROOT", str(root)), patch.object(sys, "argv", args):
                state.main()
            data = json.loads((root / "challenges/sample/state.json").read_text())
            self.assertEqual(len(data["hypotheses"]), 1)
            self.assertEqual(data["hypotheses"][0]["priority"], 0)
            self.assertEqual(data["hypotheses"][0]["status"], "open")


if __name__ == "__main__":
    unittest.main(verbosity=2)
