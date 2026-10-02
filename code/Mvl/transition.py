"""Fail-closed state-transition semantics."""
from dataclasses import dataclass
from typing import Any

from .verdict import Verdict, VerificationDomain, VerificationResult


def authorized(v: Verdict) -> bool:
    """Only ACCEPT authorizes a consequential transition."""
    return v is Verdict.ACCEPT


@dataclass
class TransitionRecord:
    authorized: bool
    verification: VerificationResult


def attempt_transition(domain: VerificationDomain, s_from: Any, s_to: Any) -> TransitionRecord:
    """Verify the transition itself: invariants receive the pair (s_from, s_to)."""
    res = domain.run((s_from, s_to))
    return TransitionRecord(authorized(res.verdict), res)
