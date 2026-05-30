from app.reconciliation.base import Reconciler, register_reconciler
from app.reconciliation.core import reconcile_transactions
from app.reconciliation.matcher import dedupe_transactions


class SimpleReconciler(Reconciler):
    name = "simple"

    def reconcile(self, transactions, **kwargs):
        # Basic flow: dedupe then run the reconciliation scaffold
        deduped, duplicates = dedupe_transactions(transactions)
        result = reconcile_transactions(deduped)
        result["duplicates"] = duplicates
        result["reconciler"] = self.name
        return result


# Register on import so loader can discover this implementation
register_reconciler(SimpleReconciler.name, SimpleReconciler)
