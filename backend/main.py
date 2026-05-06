from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.constants import DEFAULT_ADMIN_CREDITS, DEFAULT_ADMIN_EMAIL
from backend.dao.database import ensure_indexes
from backend.dao.user_dao import upsert_admin
from backend.routers import auth, caption, user

app = FastAPI(
    title="AI Caption API",
    description="Multi-layered modular backend",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(caption.router)
app.include_router(user.router)


@app.on_event("startup")
async def startup():
    await ensure_indexes()
    await upsert_admin(DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_CREDITS)

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {
        "message": "AI Caption API v2.0 - Modular Architecture",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
