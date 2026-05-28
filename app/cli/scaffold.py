import argparse
import os
from pathlib import Path


TEMPLATE_PROVIDER_PY = '''from app.providers.base import BaseProvider

class {ClassName}Provider(BaseProvider):
    def __init__(self, config_path: str = None):
        self.id = "{name}_example"
        self.name = "{Name} Example Provider"

    async def discover_accounts(self):
        return []

    async def sync_transactions(self, account, since):
        return []

    async def sync_positions(self, account):
        return []

    async def list_actions(self):
        return []

    async def execute_action(self, action_name: str, payload: dict, dry_run: bool = False):
        return {{}}

    async def match_transaction(self, optimistic_tx, provider_tx):
        return False
'''


def create_provider_scaffold(base_dir: Path, name: str):
    pkg_dir = base_dir / name
    pkg_dir.mkdir(parents=True, exist_ok=True)
    # __init__.py
    init_py = pkg_dir / "__init__.py"
    init_py.write_text(f"""from .provider import {name.capitalize()}Provider\n\ndef load_providers():\n    # Return a mapping of provider_id -> provider instance\n    p = {name.capitalize()}Provider()\n    return {{p.id: p}}\n""")

    # provider.py
    provider_py = pkg_dir / "provider.py"
    provider_py.write_text(TEMPLATE_PROVIDER_PY.format(ClassName=name.capitalize(), name=name, Name=name.capitalize()))

    # platform stubs
    for plat in ("portfolio.py", "ledger.py", "budget.py"):
        (pkg_dir / plat).write_text("""async def async_setup_%s(provider):\n    return {}\n""" % plat.split(".")[0])

    # add a data folder for sample configs
    (pkg_dir / "mock_data").mkdir(exist_ok=True)

    print(f"Created provider scaffold at: {pkg_dir}")


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new provider integration under app/providers")
    parser.add_argument("name", help="Provider package name (snake_case)")
    args = parser.parse_args()

    workspace_root = Path(__file__).resolve().parents[2]
    providers_dir = workspace_root / "app" / "providers"
    create_provider_scaffold(providers_dir, args.name)


if __name__ == "__main__":
    main()
