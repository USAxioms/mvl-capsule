import unittest

from mvl.verdict import Verdict as V, VerificationDomain
from mvl.transition import authorized, attempt_transition
from mvl.obligation import Status, LedgerEntry, is_truth, accept_consequential


class Transitions(unittest.TestCase):
    def test_only_accept_authorizes(self):
        self.assertTrue(authorized(V.ACCEPT))
        self.assertFalse(authorized(V.REJECT))
        self.assertFalse(authorized(V.UNVERIFIED))

    def setUp(self):
        self.domain = VerificationDomain(
            "transfers conserve value", "Custodian",
            [("conserved", lambda p: sum(p[0].values()) == sum(p[1].values())),
             ("no_negative", lambda p: all(v >= 0 for v in p[1].values()))])

    def test_valid_transition(self):
        r = attempt_transition(self.domain, {"a": 10, "b": 0}, {"a": 4, "b": 6})
        self.assertTrue(r.authorized)

    def test_value_created_rejected(self):
        r = attempt_transition(self.domain, {"a": 10, "b": 0}, {"a": 10, "b": 6})
        self.assertFalse(r.authorized)
        self.assertIs(r.verification.verdict, V.REJECT)

    def test_unknown_integrity_blocks(self):
        d = VerificationDomain("p", "a", [("rule_version_current", lambda p: None)])
        r = attempt_transition(d, 0, 1)
        self.assertFalse(r.authorized)
        self.assertIs(r.verification.verdict, V.UNVERIFIED)


class Obligations(unittest.TestCase):
    def test_obligation_and_unknown_not_truth(self):
        self.assertFalse(is_truth(Status.OBLIGATION))
        self.assertFalse(is_truth(Status.UNKNOWN))
        self.assertTrue(is_truth(Status.TRUE))

    def test_obligation_not_fact(self):
        self.assertFalse(LedgerEntry("auditor sign-off", Status.OBLIGATION).is_established_fact())
        self.assertTrue(LedgerEntry("balance reconciled", Status.TRUE).is_established_fact())

    def test_consequential_acceptance(self):
        self.assertTrue(accept_consequential(V.ACCEPT, 0))
        self.assertFalse(accept_consequential(V.ACCEPT, 2))
        self.assertFalse(accept_consequential(V.UNVERIFIED, 0))
        self.assertFalse(accept_consequential(V.REJECT, 0))
        with self.assertRaises(ValueError):
            accept_consequential(V.ACCEPT, -1)


if __name__ == "__main__":
    unittest.main()
