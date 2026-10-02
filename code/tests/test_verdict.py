import itertools
import unittest

from mvl.verdict import Truth3 as T, Verdict as V, verify, to_truth3, VerificationDomain

TT, FF, UN = T.TT, T.FF, T.UNKNOWN


class GoldenVectors(unittest.TestCase):
    """The same vectors as Mvl/GoldenVectors.lean."""

    def test_all_true_accepts(self):
        self.assertIs(verify([TT, TT, TT]), V.ACCEPT)

    def test_one_false_rejects(self):
        self.assertIs(verify([TT, FF, TT]), V.REJECT)

    def test_false_dominates_unknown(self):
        self.assertIs(verify([TT, FF, UN]), V.REJECT)

    def test_unknown_is_unverified(self):
        self.assertIs(verify([TT, TT, UN]), V.UNVERIFIED)

    def test_unknown_never_accept(self):
        self.assertIsNot(verify([UN]), V.ACCEPT)

    def test_empty_is_vacuous_accept(self):
        self.assertIs(verify([]), V.ACCEPT)

    def test_reject_ne_unverified(self):
        self.assertNotEqual(V.REJECT, V.UNVERIFIED)


class Exhaustive(unittest.TestCase):
    """Every invariant-result list up to length 6 (1,093 lists) obeys the specification."""

    def test_semantics(self):
        n = 0
        for k in range(7):
            for rs in itertools.product([TT, FF, UN], repeat=k):
                v = verify(rs)
                if FF in rs:
                    self.assertIs(v, V.REJECT, rs)
                elif UN in rs:
                    self.assertIs(v, V.UNVERIFIED, rs)
                else:
                    self.assertIs(v, V.ACCEPT, rs)
                if UN in rs:
                    self.assertIsNot(v, V.ACCEPT, rs)
                n += 1
        self.assertEqual(n, 1093)

    def test_order_independent(self):
        for rs in itertools.product([TT, FF, UN], repeat=4):
            for perm in itertools.permutations(rs):
                self.assertIs(verify(perm), verify(rs))


class Typing(unittest.TestCase):
    def test_bad_type_rejected(self):
        with self.assertRaises(TypeError):
            verify([TT, True])

    def test_to_truth3(self):
        self.assertIs(to_truth3(True), TT)
        self.assertIs(to_truth3(False), FF)
        self.assertIs(to_truth3(None), UN)
        with self.assertRaises(TypeError):
            to_truth3(1)


class Domains(unittest.TestCase):
    def setUp(self):
        self.inv = [("non_negative", lambda s: s >= 0), ("at_most_100", lambda s: s <= 100)]

    def test_conforming_domain(self):
        d = VerificationDomain("keep balances in range", "Custodian", self.inv)
        self.assertEqual(d.conforms(), (True, []))
        self.assertIs(d.run(42).verdict, V.ACCEPT)
        self.assertIs(d.run(150).verdict, V.REJECT)

    def test_missing_purpose_fails_closed(self):
        r = VerificationDomain("  ", "Custodian", self.inv).run(42)
        self.assertIs(r.verdict, V.UNVERIFIED)
        self.assertIn("no declared purpose", r.reasons)

    def test_missing_authority_fails_closed(self):
        r = VerificationDomain("purpose", "", self.inv).run(42)
        self.assertIs(r.verdict, V.UNVERIFIED)

    def test_empty_invariants_not_conforming(self):
        r = VerificationDomain("purpose", "Custodian", []).run(42)
        self.assertIs(r.verdict, V.UNVERIFIED)
        self.assertTrue(any("vacuous" in x for x in r.reasons))

    def test_duplicate_invariant_names(self):
        d = VerificationDomain("p", "a", [("x", lambda s: True), ("x", lambda s: True)])
        self.assertFalse(d.conforms()[0])

    def test_unknown_invariant(self):
        d = VerificationDomain("p", "a", [("known", lambda s: True), ("feed", lambda s: None)])
        self.assertIs(d.run(0).verdict, V.UNVERIFIED)

    def test_crashing_evaluator_is_unknown_not_accept(self):
        d = VerificationDomain("p", "a", [("ok", lambda s: True), ("boom", lambda s: 1 / 0)])
        r = d.run(0)
        self.assertIs(r.verdict, V.UNVERIFIED)
        self.assertTrue(any("ZeroDivisionError" in x for x in r.reasons))

    def test_contradiction_rejects(self):
        d = VerificationDomain("p", "a", [("a", lambda s: True), ("b", lambda s: False)])
        self.assertIs(d.run(0).verdict, V.REJECT)


if __name__ == "__main__":
    unittest.main()
