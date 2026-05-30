import importlib
import os
import pkgutil
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Type

# Simple registry for reconciler implementations
RECONCILIERS: Dict[str, Type['Reconciler']] = {}


class Reconciler(ABC):
    """Abstract base class for reconciliation modules.

    Implementations should subclass this and register themselves via
    `register_reconciler(name, cls)` or by importing a plugin module that
    registers on import.
    """
    name: str = "base"

    @abstractmethod
    def reconcile(self, transactions: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Run reconciliation on a list of transactions.

        Returns a dict with reconciliation results (IDs, corrections, metadata).
        """
        raise NotImplementedError()


def register_reconciler(name: str, cls: Type[Reconciler]):
    RECONCILIERS[name] = cls


def get_reconciler(name: str) -> Type[Reconciler]:
    return RECONCILIERS.get(name)


def list_reconcilers() -> List[str]:
    return list(RECONCILIERS.keys())


def load_plugins():
    """Discover and import any modules under `app.reconciliation.plugins`.

    Plugin modules should register reconciler classes at import time by
    calling `register_reconciler()`.
    """
    pkg_dir = os.path.join(os.path.dirname(__file__), "plugins")
    if not os.path.isdir(pkg_dir):
        return
    for finder, name, ispkg in pkgutil.iter_modules([pkg_dir]):
        module_name = f"app.reconciliation.plugins.{name}"
        try:
            importlib.import_module(module_name)
        except Exception:
            # ignore plugin import errors; plugins should be best-effort
            continue
