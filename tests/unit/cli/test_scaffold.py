from pathlib import Path
from app.cli.scaffold import create_provider_scaffold


def test_create_provider_scaffold(tmp_path):
    base = tmp_path / "providers"
    name = "toyprovider"
    create_provider_scaffold(base, name)

    pkg = base / name
    assert pkg.exists()
    assert (pkg / "__init__.py").exists()
    assert (pkg / "provider.py").exists()
    assert (pkg / "mock_data").exists()

    # provider.py should contain the provider class name
    text = (pkg / "provider.py").read_text()
    assert "class ToyproviderProvider" in text or "class ToyproviderProvider" in text
