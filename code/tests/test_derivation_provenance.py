import unittest

from mvl.derivation import (Representation as R, is_authoritative, Mapping, establishes_equivalence,
                            derivative_ok, Digest, compute_digest, ProofStatus, report_as_proven)
from mvl.provenance import canonical_json, digest_of, VersionLedger, ProvenanceRecord


class Derivation(unittest.TestCase):
    def test_only_canonical_is_authoritative(self):
        self.assertTrue(is_authoritative(R.CANONICAL))
        for r in (R.LEAN, R.JSONL, R.CODE_OCEAN, R.BLOCKCHAIN):
            self.assertFalse(is_authoritative(r), r)

    def test_mapping_classes(self):
        self.assertTrue(establishes_equivalence(Mapping.EXACT))
        for m in (Mapping.STRUCTURE_PRESERVING, Mapping.PROJECTION, Mapping.APPROXIMATION, Mapping.UNRESOLVED):
            self.assertFalse(establishes_equivalence(m), m)

    def test_derivative_authority(self):
        self.assertFalse(derivative_ok(1, 2))
        self.assertTrue(derivative_ok(2, 2))
        self.assertTrue(derivative_ok(2, 1))

    def test_known_sha256(self):
        self.assertEqual(compute_digest(b"").value,
                         "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        self.assertEqual(compute_digest(b"abc").value,
                         "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    def test_fabricated_digest_rejected(self):
        self.assertFalse(Digest("e3b0c442", False).admissible())
        self.assertTrue(Digest(None, False).admissible())
        self.assertTrue(compute_digest(b"x").admissible())

    def test_proof_status(self):
        self.assertTrue(report_as_proven(ProofStatus.PROVEN))
        for s in (ProofStatus.FAILED, ProofStatus.NOT_FORMALIZED, ProofStatus.NOT_YET_CHECKED):
            self.assertFalse(report_as_proven(s), s)


class Provenance(unittest.TestCase):
    def test_canonical_json_is_order_independent(self):
        self.assertEqual(canonical_json({"b": 1, "a": [2, 3]}), canonical_json({"a": [2, 3], "b": 1}))
        self.assertEqual(canonical_json({"b": 1, "a": 2}), b'{"a":2,"b":1}')

    def test_digest_changes_with_content(self):
        self.assertNotEqual(digest_of({"rule": "x"}), digest_of({"rule": "y"}))

    def test_ledger_append_only_and_chained(self):
        led = VersionLedger()
        led.append("1.0", "semantic", {"law": "v1"})
        first = led.history[0]
        led.append("1.1", "editorial", {"law": "v1", "typo": "fixed"})
        self.assertEqual(len(led.history), 2)
        self.assertEqual(led.history[0], first)               # history preserved
        self.assertEqual(led.history[1]["previous"], first["entry_digest"])
        self.assertTrue(led.verify_chain())

    def test_tampering_detected(self):
        led = VersionLedger()
        led.append("1.0", "semantic", {"law": "v1"})
        led.append("1.1", "corrective", {"law": "v1b"})
        led._entries[0]["content_digest"] = "0" * 64           # simulate altered provenance
        self.assertFalse(led.verify_chain())

    def test_change_kind_required(self):
        with self.assertRaises(ValueError):
            VersionLedger().append("2.0", "cosmetic", {})

    def test_provenance_record(self):
        rec = ProvenanceRecord("spec.tex", "USAC", "2026-10", "tex->python", digest_of("a"), None, "py3", "ACCEPT")
        self.assertEqual(rec.to_dict()["derivative_digest"], None)


if __name__ == "__main__":
    unittest.main()
