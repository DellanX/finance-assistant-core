from fastapi import APIRouter
from app.providers.registry import active_providers
from app.core.schemas import PortfolioResponse

router = APIRouter()
@router.get("", response_model=PortfolioResponse)
async def get_portfolio():
    holdings = []
    cash_balance = 0.0
    investment_balance = 0.0

    for provider_id, provider in active_providers.items():
        accounts = await provider.discover_accounts()
        for acc in accounts:
            # acc may be a Pydantic model
            if hasattr(acc, "model_dump"):
                accd = acc.model_dump()
            elif isinstance(acc, dict):
                accd = acc
            else:
                try:
                    accd = dict(acc)
                except Exception:
                    accd = {}

            acc_type = accd.get("type")
            balance = accd.get("balance", 0.0)

            if acc_type == "depository":
                cash_balance += balance
            elif acc_type == "investment":
                cash_balance += balance

            positions = await provider.sync_positions(acc)
            for pos in positions:
                if hasattr(pos, "model_dump"):
                    posd = pos.model_dump()
                elif isinstance(pos, dict):
                    posd = pos
                else:
                    try:
                        posd = dict(pos)
                    except Exception:
                        posd = {}

                qty = posd.get("quantity", 0.0)
                curr_price = posd.get("current_price", 0.0)
                cost_basis = posd.get("cost_basis", 0.0)
                val = qty * curr_price
                cost = qty * cost_basis
                gain = val - cost
                gain_pct = (gain / cost * 100) if cost > 0 else 0.0

                holdings.append({
                    "symbol": posd.get("symbol"),
                    "quantity": qty,
                    "cost_basis": cost_basis,
                    "current_price": curr_price,
                    "value": val,
                    "gain": gain,
                    "gain_pct": gain_pct,
                    "account_name": accd.get("name"),
                    "provider_name": provider.name
                })
                investment_balance += val

    total_value = cash_balance + investment_balance
    resp = {
        "summary": {
            "total_value": total_value,
            "cash_balance": cash_balance,
            "investment_balance": investment_balance,
        },
        "holdings": holdings,
    }
    # Return a typed PortfolioResponse instance
    from app.core.schemas import PortfolioResponse

    return PortfolioResponse(**resp)

