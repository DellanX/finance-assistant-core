import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.providers import registry

app = FastAPI(title="Finance Assistant API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def _on_startup():
    # Start provider coordinators (non-blocking start)
    registry.start_all_coordinators()


@app.on_event("shutdown")
async def _on_shutdown():
    # Await stopping any provider coordinators
    await registry.stop_all_coordinators()


@app.get("/health")
def health_check():
    # Basic app health plus provider coordinator statuses
    provider_status = {}
    try:
        provider_status = registry.coordinator_statuses()
    except Exception:
        provider_status = {"error": "failed to collect provider statuses"}

    return {"status": "ok", "providers": provider_status}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
