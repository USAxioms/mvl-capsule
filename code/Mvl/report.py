"""Build the capsule's verification report.

The report has a deterministic core (golden-vector verdicts, artifact digests,
example domain runs) whose SHA-256 is recorded so that independent reruns can
be compared, plus an environment section that is excluded from that digest.
"""
import json
import platform
import sys
from pathlib import Path

from . import __version__, SPEC_VERSION
from .derivation import compute_digest
from .provenance import canonical_json, digest_of
from .transition import attempt_transition
from .verdict import Truth3 as T, verify, VerificationDomain

GOLDEN = [
    ("all true", [T.TT, T.TT, T.TT]),
    ("one false", [T.TT, T.FF, T.TT]),
    ("false dominates unknown", [T.TT, T.FF, T.UNKNOWN]),
    ("unknown without false", [T.TT, T.TT, T.UNKNOWN]),
    ("single unknown", [T.UNKNOWN]),
    ("empty (vacuous; non-conforming domain)", []),
]


def example_domain() -> VerificationDomain:
    return VerificationDomain(
        purpose="Transfers between two accounts conserve total value and keep balances non-negative.",
        authority="Declared custodian of the example domain",
        invariants=[("conserved", lambda p: sum(p[0].values()) == sum(p[1].values())),
                    ("non_negative", lambda p: all(v >= 0 for v in p[1].values())),
                    ("rate_source_available", lambda p: p[1].get("_rate_known", True) or None)])


def core(data_dir: Path) -> dict:
    artifacts = {}
    for f in sorted(data_dir.glob("*")):
        if f.is_file():
            artifacts[f.name] = compute_digest(f.read_bytes()).value
    d = example_domain()
    runs = {
        "valid transfer": attempt_transition(d, {"a": 10, "b": 0}, {"a": 4, "b": 6}),
        "value created": attempt_transition(d, {"a": 10, "b": 0}, {"a": 10, "b": 6}),
        "rate source unavailable": attempt_transition(d, {"a": 10, "b": 0}, {"a": 4, "b": 6, "_rate_known": False}),
    }
    return {
        "implementation_version": __version__,
        "canonical_spec_version": SPEC_VERSION,
        "artifact_sha256": artifacts,
        "golden_vectors": [{"case": n, "results": [r.value for r in rs], "verdict": verify(rs).value}
                           for n, rs in GOLDEN],
        "example_domain_runs": {k: {"authorized": v.authorized, **v.verification.to_dict()}
                                for k, v in runs.items()},
    }


def build(data_dir: Path, tests: dict) -> dict:
    c = core(data_dir)
    return {
        "core": c,
        "core_sha256": compute_digest(canonical_json(c)).value,
        "tests": tests,
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "status_note": ("Computational checks of a derivative implementation. Not a legal-validity "
                        "determination and not a proof of any proposition outside the tested domain."),
    }


if __name__ == "__main__":
    data_dir, out, tests_json = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    rep = build(data_dir, json.loads(tests_json.read_text()))
    out.write_text(json.dumps(rep, indent=2, sort_keys=True) + "\n")
    print("core_sha256", rep["core_sha256"])
