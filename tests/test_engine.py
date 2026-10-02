import json
import unittest
from cryptolab import *

EXAMPLE = json.loads(
    '{"reserve_x": 1000000, "reserve_y": 2000000, "lp_supply": 1000000, "actions": [{"type": "swap", "direction": "x_to_y", "amount": 10000}]}'
)


class EngineTests(unittest.TestCase):
    def test_swap_invariant(self):
        r = analyze(EXAMPLE)["history"][0]
        self.assertGreaterEqual(r["k"], r["k_before"])
        self.assertEqual(r["output"], 19743)

    def test_slippage(self):
        d = {**EXAMPLE, "actions": [{**EXAMPLE["actions"][0], "min_output": 999999}]}
        with self.assertRaises(ValueError):
            analyze(d)

    def test_liquidity_roundtrip(self):
        d = {
            **EXAMPLE,
            "actions": [
                {"type": "add_liquidity", "amount_x": 100000, "amount_y": 200000},
                {"type": "remove_liquidity", "shares": 100000},
            ],
        }
        r = analyze(d)
        self.assertEqual(r["reserve_x"], 1000000)
        self.assertEqual(r["lp_supply"], 1000000)

    def test_deterministic(self):
        self.assertEqual(analyze(EXAMPLE), analyze(EXAMPLE))

    def test_cli_json(self):
        import subprocess, sys

        result = subprocess.run(
            [sys.executable, "-m", "cryptolab", "examples/input.json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), analyze(EXAMPLE))

    def test_cli_csv(self):
        import subprocess, sys, csv, io

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "cryptolab",
                "examples/input.json",
                "--format",
                "csv",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            list(csv.reader(io.StringIO(result.stdout)))[0], ["path", "value"]
        )

    def test_duplicate_json_keys(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"a":1,"a":2}')
            with self.assertRaises(ValueError):
                load_input(path)

    def test_atomic_output(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "out.json"
            self.assertEqual(main(["examples/input.json", "--output", str(path)]), 0)
            self.assertEqual(json.loads(path.read_text()), analyze(EXAMPLE))

    def test_input_unchanged(self):
        import copy

        before = copy.deepcopy(EXAMPLE)
        analyze(EXAMPLE)
        self.assertEqual(before, EXAMPLE)


if __name__ == "__main__":
    unittest.main()
