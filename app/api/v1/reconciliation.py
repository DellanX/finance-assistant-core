from fastapi import APIRouter, HTTPException
from typing import Any, Dict
from app.reconciliation.base import load_plugins, list_reconcilers, get_reconciler
from app.reconciliation import store
from app.api.v1.types import ReconcilerListResponse


router = APIRouter()

# Ensure plugins are discovered on import
load_plugins()


@router.get("", response_model=ReconcilerListResponse)
def list_available_reconcilers():
    return {"reconcilers": list_reconcilers()}


@router.post("")
def run_reconciliation(payload: Dict[str, Any]):
    """Run a reconciler by name.

    Payload: { "reconciler": "simple", "transactions": [...] }
    """
    name = payload.get("reconciler")
    if not name:
        raise HTTPException(status_code=400, detail="reconciler is required")

    cls = get_reconciler(name)
    if cls is None:
        raise HTTPException(status_code=404, detail="reconciler not found")

    transactions = payload.get("transactions") or []
    try:
        inst = cls()
        res = inst.reconcile(transactions)
        # Persist run record
        run_record = {
            "reconciliation_id": res.get("reconciliation_id"),
            "reconciler": name,
            "transactions": transactions,
            "result": res,
            "duplicates": res.get("duplicates", []),
            "corrections": [],
        }
        try:
            store.save_run(run_record)
        except Exception:
            # best-effort persistence; ignore failures but return result
            pass
        return res
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/history")
def list_history():
    return store.list_runs()


@router.get("/history/{run_id}")
def get_history(run_id: str):
    rec = store.get_run(run_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="run not found")
    return rec


@router.post("/{run_id}/corrections")
def post_corrections(run_id: str, payload: Dict[str, Any]):
    corrections = payload.get("corrections") or []
    rec = store.append_corrections(run_id, corrections)
    if rec is None:
        raise HTTPException(status_code=404, detail="run not found")
    return rec
