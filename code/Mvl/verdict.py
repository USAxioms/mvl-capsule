"""Verification semantics: Verify : S x L -> {ACCEPT, REJECT, UNVERIFIED}."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Iterable, List, Optional, Tuple


class Truth3(Enum):
    TT = "true"
    FF = "false"
    UNKNOWN = "unknown"


class Verdict(Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    UNVERIFIED = "UNVERIFIED"


def verify(results: Iterable[Truth3]) -> Verdict:
    """Any FF => REJECT; else any UNKNOWN => UNVERIFIED; else ACCEPT.

    Note: an empty result list is vacuously ACCEPT. A conforming
    verification domain therefore must declare at least one mandatory
    invariant (see VerificationDomain.conforms).
    """
    rs = list(results)
    for r in rs:
        if not isinstance(r, Truth3):
            raise TypeError(f"invariant result must be Truth3, got {r!r}")
    if any(r is Truth3.FF for r in rs):
        return Verdict.REJECT
    if any(r is Truth3.UNKNOWN for r in rs):
        return Verdict.UNVERIFIED
    return Verdict.ACCEPT


def to_truth3(value: Optional[bool]) -> Truth3:
    """True -> TT, False -> FF, None -> UNKNOWN. Anything else is a typing defect."""
    if value is True:
        return Truth3.TT
    if value is False:
        return Truth3.FF
    if value is None:
        return Truth3.UNKNOWN
    raise TypeError(f"invariant must return True, False, or None; got {value!r}")


Invariant = Tuple[str, Callable[[Any], Optional[bool]]]


@dataclass
class VerificationResult:
    verdict: Verdict
    results: List[Tuple[str, Truth3]]
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"verdict": self.verdict.value,
                "results": [[n, r.value] for n, r in self.results],
                "reasons": list(self.reasons)}


@dataclass
class VerificationDomain:
    """A declared verification domain. Purpose and authority precede computation."""
    purpose: str
    authority: str
    invariants: List[Invariant]
    version: str = "1"

    def conforms(self) -> Tuple[bool, List[str]]:
        reasons = []
        if not self.purpose.strip():
            reasons.append("no declared purpose")
        if not self.authority.strip():
            reasons.append("no identified authority")
        if not self.invariants:
            reasons.append("no mandatory invariants declared (acceptance would be vacuous)")
        names = [n for n, _ in self.invariants]
        if len(names) != len(set(names)):
            reasons.append("duplicate invariant names")
        return (not reasons, reasons)

    def run(self, state: Any) -> VerificationResult:
        ok, reasons = self.conforms()
        if not ok:
            # Fail closed: a non-conforming domain cannot establish anything.
            return VerificationResult(Verdict.UNVERIFIED, [], reasons)
        results = []
        for name, fn in self.invariants:
            try:
                r = to_truth3(fn(state))
            except Exception as e:  # an evaluator that fails cannot establish its condition
                r = Truth3.UNKNOWN
                reasons.append(f"{name}: evaluation failed ({type(e).__name__})")
            results.append((name, r))
        return VerificationResult(verify(r for _, r in results), results, reasons)
