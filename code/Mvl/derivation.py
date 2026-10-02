"""Derivation, authority, semantic mappings, digests, and proof status."""
import hashlib
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Representation(Enum):
    CANONICAL = "canonical"
    LEAN = "lean"
    JSONL = "jsonl"
    CODE_OCEAN = "code_ocean"
    BLOCKCHAIN = "blockchain"


def is_authoritative(r: Representation) -> bool:
    """Only the canonical semantic specification carries normative authority."""
    return r is Representation.CANONICAL


class Mapping(Enum):
    EXACT = "exact"
    STRUCTURE_PRESERVING = "structure_preserving"
    PROJECTION = "projection"
    APPROXIMATION = "approximation"
    UNRESOLVED = "unresolved"


def establishes_equivalence(m: Mapping) -> bool:
    return m is Mapping.EXACT


def derivative_ok(source_rank: int, derivative_rank: int) -> bool:
    """Integrity rule 1: no derivative may contain more authority than its source."""
    return derivative_rank <= source_rank


@dataclass(frozen=True)
class Digest:
    value: Optional[str]
    computed: bool

    def admissible(self) -> bool:
        """A digest may be represented only when actually computed."""
        return self.value is None or self.computed


def compute_digest(data: bytes) -> Digest:
    return Digest(hashlib.sha256(data).hexdigest(), True)


class ProofStatus(Enum):
    PROVEN = "proven"
    FAILED = "failed"
    NOT_FORMALIZED = "not_formalized"
    NOT_YET_CHECKED = "not_yet_checked"


def report_as_proven(s: ProofStatus) -> bool:
    return s is ProofStatus.PROVEN
