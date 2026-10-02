"""Run the suite, write a human-readable log and a JSON summary."""
import json
import sys
import unittest
from pathlib import Path

out = Path(sys.argv[1])
here = Path(__file__).resolve().parent
suite = unittest.defaultTestLoader.discover(str(here / "tests"), top_level_dir=str(here))
with open(out / "test_report.txt", "w") as log:
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
summary = {"ran": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
           "skipped": len(result.skipped), "passed": result.wasSuccessful()}
(out / "test_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary))
sys.exit(0 if result.wasSuccessful() else 1)
