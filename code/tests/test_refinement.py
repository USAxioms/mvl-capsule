import random
import unittest

from mvl.refinement import R3, run_r3, valid_refinement, InvalidRefinement, NonConvergence


def defect_resolver():
    """A canonical state is (meaning, defects). Each step resolves one defect; meaning is untouched.
    Material change = the set of defects changed. Wording changes are not material."""
    step = lambda c: (c[0], c[1][1:], c[2] + 1)            # c[2] counts editorial passes
    material = lambda a, b: sorted(set(a[1]) ^ set(b[1]))
    preserves = lambda a, b: a[0] == b[0]
    return R3(step, material, preserves)


class R3Tests(unittest.TestCase):
    def test_reaches_fixed_point(self):
        r = defect_resolver()
        trace = run_r3(r, ("meaning", ["contradiction", "ambiguity", "missing dependency"], 0), 10)
        self.assertEqual(trace.iterations, 3)
        self.assertTrue(r.is_fixed(trace.states[-1]))
        self.assertEqual(trace.states[-1][1], [])

    def test_editorial_change_does_not_continue(self):
        r = defect_resolver()
        c = ("meaning", [], 0)
        self.assertTrue(r.is_fixed(c))        # step changes the editorial counter only
        self.assertEqual(run_r3(r, c, 5).iterations, 0)

    def test_terminates_within_defect_count(self):
        rng = random.Random(7)
        r = defect_resolver()
        for _ in range(200):
            defects = [f"d{i}" for i in range(rng.randint(0, 25))]
            trace = run_r3(r, ("m", defects, 0), 100)
            self.assertLessEqual(trace.iterations, len(defects))
            self.assertTrue(r.is_fixed(trace.states[-1]))

    def test_meaning_change_invalid(self):
        bad = R3(lambda c: ("changed meaning", c[1][1:], 0),
                 lambda a, b: sorted(set(a[1]) ^ set(b[1])),
                 lambda a, b: a[0] == b[0])
        with self.assertRaises(InvalidRefinement):
            run_r3(bad, ("meaning", ["contradiction"], 0), 5)
        self.assertFalse(valid_refinement(True, False))
        self.assertTrue(valid_refinement(True, True))

    def test_non_convergence_detected(self):
        churn = R3(lambda c: c + 1, lambda a, b: ["changed"], lambda a, b: True)
        with self.assertRaises(NonConvergence):
            run_r3(churn, 0, 20)


if __name__ == "__main__":
    unittest.main()
