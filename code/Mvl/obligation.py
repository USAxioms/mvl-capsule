"""TRUE / FALSE / UNKNOWN / OBLIGATION, and consequential acceptance."""
from dataclasses import dataclass
from enum import Enum

from .verdict import Verdict


class Status(Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    UNKNOWN = "UNKNOWN"
    OBLIGATION = "OBLIGATION"


def is_truth(s: Status) -> bool:
    return s is Status.TRUE


@dataclass(frozen=True)
class LedgerEntry:
    claim: str
    status: Status

    def is_established_fact(self) -> bool:
        return is_truth(self.status)


def accept_consequential(v: Verdict, open_obligations: int) -> bool:
    """Consequential acceptance requires ACCEPT and every mandatory obligation satisfied."""
    if open_obligations < 0:
        raise ValueError("obligation count cannot be negative")
    return v is Verdict.ACCEPT and open_obligations == 0
