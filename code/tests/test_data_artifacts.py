"""Checks on the canonical source and the JSONL derivative shipped in /data."""
import json
import re
import unittest

from mvl.derivation import compute_digest
from tests._paths import SPEC_TEX, JSONL


class CanonicalSource(unittest.TestCase):
    def test_present_and_declares_direction(self):
        text = SPEC_TEX.read_text(encoding="utf-8")
        self.assertIn("BEGIN WITH PURPOSE. END IN TRUTH.", text)
        for macro in (r"\Accept", r"\Reject", r"\Unknown", r"\Obligation"):
            self.assertIn(macro, text)

    def test_digest_is_computed(self):
        d = compute_digest(SPEC_TEX.read_bytes())
        self.assertTrue(d.computed)
        self.assertRegex(d.value, r"^[0-9a-f]{64}$")


class JsonlDerivative(unittest.TestCase):
    def setUp(self):
        self.rows = [json.loads(l) for l in JSONL.read_text(encoding="utf-8").splitlines() if l.strip()]

    def test_sixty_rows(self):
        self.assertEqual(len(self.rows), 60)

    def test_structure(self):
        for r in self.rows:
            self.assertEqual([m["role"] for m in r["messages"]], ["system", "user", "assistant"])
            self.assertTrue(all(m["content"].strip() for m in r["messages"]))

    def test_unique_questions(self):
        qs = [r["messages"][1]["content"] for r in self.rows]
        self.assertEqual(len(qs), len(set(qs)))

    def test_no_fabricated_full_hashes(self):
        """No assistant answer may present a 64-hex digest it did not compute."""
        for r in self.rows:
            self.assertIsNone(re.search(r"\b[0-9a-f]{64}\b", r["messages"][2]["content"]))


if __name__ == "__main__":
    unittest.main()
