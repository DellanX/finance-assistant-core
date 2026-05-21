import uvicorn
from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(title="Finance Assistant API", version="0.1.0")

app.include_router(api_router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
