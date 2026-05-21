from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_portfolios():
    return []
