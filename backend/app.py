from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router as routes_router

app = FastAPI()

# Allow all origins/methods/headers for rapid prototyping. tighten before production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}