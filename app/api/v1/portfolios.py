from fastapi import APIRouter
from app.providers.registry import active_providers

router = APIRouter()

@router.get("")
async def get_portfolio():
    holdings = []
    cash_balance = 0.0
    investment_balance = 0.0
    
    for provider_id, provider in active_providers.items():
        accounts = await provider.discover_accounts()
        for acc in accounts:
            acc_type = acc.get("type")
            balance = acc.get("balance", 0.0)
            
            if acc_type == "depository":
                cash_balance += balance
            elif acc_type == "investment":
                # We can treat investment cash/settled balance as cash, but let's see. 
                # In volatile_crypto, the balance is 12500.00 USD. Let's include it in cash balance.
                cash_balance += balance
                
            positions = await provider.sync_positions(acc)
            for pos in positions:
                qty = pos.get("quantity", 0.0)
                curr_price = pos.get("current_price", 0.0)
                cost_basis = pos.get("cost_basis", 0.0)
                val = qty * curr_price
                cost = qty * cost_basis
                gain = val - cost
                gain_pct = (gain / cost * 100) if cost > 0 else 0.0
                
                holdings.append({
                    "symbol": pos.get("symbol"),
                    "quantity": qty,
                    "cost_basis": cost_basis,
                    "current_price": curr_price,
                    "value": val,
                    "gain": gain,
                    "gain_pct": gain_pct,
                    "account_name": acc.get("name"),
                    "provider_name": provider.name
                })
                investment_balance += val
                
    total_value = cash_balance + investment_balance
    return {
        "summary": {
            "total_value": total_value,
            "cash_balance": cash_balance,
            "investment_balance": investment_balance
        },
        "holdings": holdings
    }

