"""Locate /data both in a Code Ocean capsule and in a local checkout."""
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODE = HERE.parent
DATA = Path(os.environ.get("MVL_DATA_DIR", "/data" if Path("/data").is_dir() else CODE.parent / "data"))
SPEC_TEX = DATA / "Machine_Verifiable_Law_Canonical_Specification.tex"
JSONL = DATA / "mvl_train.jsonl"
