#!/usr/bin/env python3
"""Tests for ai-excited-01 v2: determinism, size, dimensions."""
import hashlib
import os
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_main(out_dir):
    env = dict(os.environ, MAKEFUN_OUTPUT_DIR=out_dir)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "main.py")],
                       env=env, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    return os.path.join(out_dir, "entry.png")


class TestEntry(unittest.TestCase):
    def test_deterministic_and_valid(self):
        with tempfile.TemporaryDirectory() as d1, \
                tempfile.TemporaryDirectory() as d2:
            p1 = run_main(d1)
            p2 = run_main(d2)
            b1 = open(p1, "rb").read()
            b2 = open(p2, "rb").read()
            self.assertEqual(hashlib.sha256(b1).hexdigest(),
                             hashlib.sha256(b2).hexdigest(),
                             "two runs must write identical bytes")
            self.assertTrue(b1.startswith(b"\x89PNG\r\n\x1a\n"),
                            "must be a PNG")
            w, h = struct.unpack(">II", b1[16:24])
            self.assertEqual((w, h), (1024, 1024))
            self.assertLessEqual(len(b1), 1048576,
                                 "must be at most 1 MiB")


if __name__ == "__main__":
    unittest.main()
