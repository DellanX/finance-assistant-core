from fastapi.testclient import TestClient
import pytest

from app import main as app_main


@pytest.fixture(autouse=True)
def client():
    with TestClient(app_main.app) as c:
        yield c
