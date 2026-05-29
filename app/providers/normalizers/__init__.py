"""Compatibility shim exposing the helpers API under the old normalizers path.

This keeps older imports working while the implementation lives under
`app.providers.helpers`.
"""
from app.providers.helpers import *  # re-export helpers under normalizers

try:
    from app.providers.helpers import __all__ as __helpers_all__
    __all__ = list(__helpers_all__)
except Exception:
    __all__ = [
        "normalize_transaction",
        "normalize_transactions",
        "normalize_position",
        "normalize_positions",
    ]
