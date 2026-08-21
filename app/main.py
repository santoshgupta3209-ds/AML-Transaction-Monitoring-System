from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.api.customer import router as customer_router
from app.api.notifications import router as notifications_router
from app.api.transactions import router as transactions_router
from app.config import settings
from app.database import SessionLocal, init_db
from app.models.user import User
from app.security import hash_password


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Based Anti-Money Laundering Transaction Monitoring System",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(customer_router)
app.include_router(notifications_router)
app.include_router(transactions_router)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# DATABASE / STARTUP
# ============================================================

@app.on_event("startup")
def startup_event():
    init_db()
    db = SessionLocal()
    try:
        admin_user = (
            db.query(User)
            .filter(User.username == "santosh7102005")
            .first()
        )

        if not admin_user:
            new_admin = User(
                username="santosh7102005",
                email="admin@example.com",
                password_hash=hash_password("TDDS023A"),
                role="ADMIN"
            )
            db.add(new_admin)
            db.commit()
    finally:
        db.close()


# ============================================================
# HOME
# ============================================================

@app.get("/api")
def home():

    return {
        "message": "AI-Based AML Transaction Monitoring System",
        "status": "running",
        "version": "1.0.0"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# ============================================================
# TEST ML MODEL
# ============================================================

@app.get("/ml/status")
def ml_status():

    return {
        "ml_model": "trained",
        "status": "ready"
    }