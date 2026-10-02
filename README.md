# Machine-Verifiable Law — Code Ocean Reproducibility Capsule

Executable derivative of the **Foundational Canonical Specification for Machine-Verifiable Law** (Universal Standard Axiom Corporation, October 2026). Under the specification's derivation rule, this capsule is *executable evidence of a defined canonical procedure*. It carries no authority of its own, and its results apply only within the tested domain.

BEGIN WITH PURPOSE. END IN TRUTH.

## Layout

| Path | Contents |
|---|---|
| `code/run` | Code Ocean entry point |
| `code/mvl/` | Reference implementation (Python 3 standard library only) |
| `code/tests/` | Test suite (54 tests) |
| `data/` | Canonical specification source (.tex) and the 60-row JSONL derivative |
| `environment/Dockerfile` | Reference environment for local runs |
| `results/` | Written by each run |

## Run

**On Code Ocean:** upload `code/`, `data/`, and `environment/`; choose any Python 3.10+ starter environment (no packages needed); click **Reproducible Run**.

**Locally:**
```bash
cd code && ./run          # writes to ../results
# or
docker build -t mvl-capsule . -f environment/Dockerfile && docker run --rm mvl-capsule
```

## What each run produces

| File | Contents |
|---|---|
| `test_report.txt` | Verbose log of every test |
| `test_summary.json` | Counts of tests run, failures, errors |
| `verification_report.json` | Golden-vector verdicts, example-domain runs, SHA-256 of every `data/` file, and `core_sha256` |

The run builds the deterministic report core twice and fails if the two digests differ.

## Modules

| Module | Specification |
|---|---|
| `verdict.py` | Verify → ACCEPT / REJECT / UNVERIFIED; declared domains with purpose, authority, invariants; fail closed |
| `transition.py` | Only ACCEPT authorizes a consequential transition |
| `obligation.py` | TRUE / FALSE / UNKNOWN / OBLIGATION; consequential acceptance |
| `refinement.py` | R³ with declared material-change relation; fixed point; diminishing-returns stop; meaning-change and non-convergence detection |
| `derivation.py` | Derivative authority, mapping classes, computed-only digests, proof status |
| `provenance.py` | Canonical serialization; append-only, hash-chained version ledger |
| `wad.py` | Optional WAD-18 fixed-point profile |

## Test suite (54 tests)

- **Golden vectors** identical to the Lean 4 repository's.
- **Exhaustive check** of all 1,093 invariant-result lists up to length 6, plus order independence.
- **Fail-closed domains:** missing purpose, missing authority, empty or duplicate invariants, unknown results, and crashing evaluators all yield UNVERIFIED, never ACCEPT.
- **Transitions and obligations.**
- **R³:** fixed point reached; editorial changes do not count as refinement; termination within the defect count (200 randomized cases); unauthorized meaning change and non-convergence detected.
- **Derivation and provenance:** only the canonical source is authoritative; known SHA-256 test vectors; fabricated digests rejected; ledger history preserved; tampering detected.
- **WAD-18:** 2,000 randomized cases cross-checked against arbitrary-precision decimals.
- **Data artifacts:** the canonical source declares its governing direction; the JSONL derivative has 60 well-formed, unique rows and presents no uncomputed 64-hex digest.
- **Reproducibility:** the report core is identical across independent builds.

## Reference run

Recorded when the capsule was built (Python 3.12.3):

| Item | Value |
|---|---|
| Tests | 54 run, 0 failures, 0 errors |
| `core_sha256` | `ea6ef13c345d290c69bb218c175d0711da9922312a9c8b0fcf6f658ea73ae469` |
| SHA-256 of the specification source (.tex) | `27e05542045b67a80def62193cc6208d76ce334cf4532ea87a3060b4d1e9c2ee` |
| SHA-256 of `mvl_train.jsonl` | `15d783a367c2b739f2729fa0a733b5c067c3fa07a49a8f447c6f1133335be6b9` |

A rerun with the same `data/` files should reproduce `core_sha256` exactly. If `data/` changes, the digests change, as they should.

## Scope

These are computational checks of a derivative implementation. They are not a determination of legal validity, and a passing test is not proof of any proposition outside its tested domain.

**Vacuous acceptance:** `verify([])` returns ACCEPT because no mandatory condition is unmet. A `VerificationDomain` with no declared invariants is therefore treated as non-conforming and returns UNVERIFIED.

No DOI is assigned yet. Record the Code Ocean DOI here only after the capsule is published.
