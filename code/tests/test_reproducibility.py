import unittest

from mvl.report import core
from mvl.provenance import digest_of
from tests._paths import DATA


class Reproducibility(unittest.TestCase):
    def test_core_identical_across_runs(self):
        a, b = core(DATA), core(DATA)
        self.assertEqual(a, b)
        self.assertEqual(digest_of(a), digest_of(b))

    def test_expected_verdicts(self):
        runs = core(DATA)["example_domain_runs"]
        self.assertEqual(runs["valid transfer"]["verdict"], "ACCEPT")
        self.assertTrue(runs["valid transfer"]["authorized"])
        self.assertEqual(runs["value created"]["verdict"], "REJECT")
        self.assertEqual(runs["rate source unavailable"]["verdict"], "UNVERIFIED")
        self.assertFalse(runs["rate source unavailable"]["authorized"])


if __name__ == "__main__":
    unittest.main()
