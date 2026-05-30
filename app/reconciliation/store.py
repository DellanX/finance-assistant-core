import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional
from app.reconciliation.matcher import apply_corrections


# Default data directory next to this module
DATA_DIR = Path(__file__).parent / "data"


def _ensure_dir() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def _run_path(run_id: str) -> Path:
    return _ensure_dir() / f"run_{run_id}.json"


def save_run(record: Dict[str, Any]) -> Dict[str, Any]:
    """Persist a reconciliation run record. Must include `reconciliation_id`."""
    rid = record.get("reconciliation_id")
    if not rid:
        raise ValueError("record must include reconciliation_id")
    p = _run_path(rid)
    # ensure timestamps
    if "created_at" not in record:
        record["created_at"] = datetime.utcnow().isoformat()
    with open(p, "w") as f:
        json.dump(record, f, indent=2)
    return record


def list_runs() -> List[Dict[str, Any]]:
    d = _ensure_dir()
    out = []
    for p in sorted(d.glob("run_*.json")):
        try:
            with open(p) as f:
                rec = json.load(f)
            out.append({"reconciliation_id": rec.get("reconciliation_id"), "reconciler": rec.get("reconciler"), "created_at": rec.get("created_at")})
        except Exception:
            continue
    return out


def get_run(run_id: str) -> Optional[Dict[str, Any]]:
    p = _run_path(run_id)
    if not p.exists():
        return None
    with open(p) as f:
        return json.load(f)


def append_corrections(run_id: str, corrections: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    rec = get_run(run_id)
    if rec is None:
        return None
    # ensure corrections list
    cur = rec.get("corrections") or []
    cur.extend(corrections)
    rec["corrections"] = cur
    # apply corrections to transactions if present
    if rec.get("transactions"):
        rec["transactions"] = apply_corrections(rec["transactions"], corrections)
    with open(_run_path(run_id), "w") as f:
        json.dump(rec, f, indent=2)
    return rec
