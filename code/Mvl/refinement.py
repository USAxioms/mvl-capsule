"""R3: Recursive Pursuit of Absolute Truth.

C_{n+1} = R3(C_n). Refinement stops when an iteration produces no material
change under the declared canonical comparison relation (Delta = empty).
"""
from dataclasses import dataclass, field
from typing import Any, Callable, List


class InvalidRefinement(Exception):
    """A refinement changed canonical meaning without authorization."""


class NonConvergence(Exception):
    """Refinement did not reach a fixed point within the declared bound."""


@dataclass
class R3:
    step: Callable[[Any], Any]
    material_changes: Callable[[Any, Any], List[str]]   # Delta(C_n, C_{n+1}) under ==_can
    preserves_meaning: Callable[[Any, Any], bool]

    def is_fixed(self, c: Any) -> bool:
        return not self.material_changes(c, self.step(c))


@dataclass
class RefinementTrace:
    states: List[Any] = field(default_factory=list)
    deltas: List[List[str]] = field(default_factory=list)

    @property
    def iterations(self) -> int:
        return len(self.deltas)


def valid_refinement(defect_reduced: bool, semantic_preserved: bool) -> bool:
    return defect_reduced and semantic_preserved


def run_r3(r3: R3, c0: Any, max_iterations: int) -> RefinementTrace:
    """Iterate until Delta is empty. Raises on unauthorized meaning change or non-convergence."""
    trace = RefinementTrace(states=[c0])
    c = c0
    for _ in range(max_iterations + 1):
        nxt = r3.step(c)
        delta = r3.material_changes(c, nxt)
        if not delta:
            return trace                       # fixed point: R3(C*) ==_can C*
        if not r3.preserves_meaning(c, nxt):
            raise InvalidRefinement("defect removed by changing canonical meaning")
        trace.deltas.append(delta)
        trace.states.append(nxt)
        c = nxt
    raise NonConvergence(f"no fixed point within {max_iterations} iterations")
