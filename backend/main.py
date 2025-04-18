from fastapi import FastAPI
from routes.organization import router as organization_router
from routes.user import router as user_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for strict mode
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ These must be prefixed with /api
app.include_router(organization_router, prefix="/api")
app.include_router(user_router, prefix="/api")
