"""Canonical serialization, provenance records, and append-only versioning."""
import json
from dataclasses import dataclass, asdict
from typing import Any, List, Optional

from .derivation import compute_digest


def canonical_json(obj: Any) -> bytes:
    """Deterministic serialization: sorted keys, no whitespace, UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest_of(obj: Any) -> str:
    return compute_digest(canonical_json(obj)).value


@dataclass(frozen=True)
class ProvenanceRecord:
    source: str
    authority: str
    version: str
    transformation: str
    canonical_digest: Optional[str]
    derivative_digest: Optional[str]
    environment: str
    result: str

    def to_dict(self) -> dict:
        return asdict(self)


VALID_CHANGE_KINDS = ("semantic", "structural", "representational", "editorial", "corrective")


class VersionLedger:
    """Append-only: supersession never erases historical provenance."""

    def __init__(self) -> None:
        self._entries: List[dict] = []

    def append(self, version: str, change_kind: str, content: Any) -> dict:
        if change_kind not in VALID_CHANGE_KINDS:
            raise ValueError(f"change kind must be one of {VALID_CHANGE_KINDS}")
        prev = self._entries[-1]["entry_digest"] if self._entries else None
        entry = {"version": version, "change_kind": change_kind,
                 "content_digest": digest_of(content), "previous": prev}
        entry["entry_digest"] = digest_of(entry)
        self._entries.append(entry)
        return dict(entry)

    @property
    def history(self) -> List[dict]:
        return [dict(e) for e in self._entries]

    def verify_chain(self) -> bool:
        prev = None
        for e in self._entries:
            body = {k: v for k, v in e.items() if k != "entry_digest"}
            if e["previous"] != prev or digest_of(body) != e["entry_digest"]:
                return False
            prev = e["entry_digest"]
        return True
