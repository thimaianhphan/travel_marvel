from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as routes_router

app = FastAPI()
# Allows all origins, methods, and headers, only for development
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