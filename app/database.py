from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


# ==========================================
# Database URL
# ==========================================

DATABASE_URL = settings.DATABASE_URL


# ==========================================
# SQLAlchemy Engine
# =========================================

engine_kwargs = {
    "pool_pre_ping": True,
    "pool_recycle": 280
}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    **engine_kwargs
)


# ==========================================
# Database Session
# ==========================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==========================================
# Base Model
# ==========================================

Base = declarative_base()


# ==========================================
# Database Dependency
# ==========================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==========================================
# Initialize Database
# ==========================================

def init_db():

    # Models will be imported in Step 3.

    from app.models import user
    from app.models import customer
    from app.models import account
    from app.models import transaction
    from app.models import aml_alert
    from app.models import notification
    from app.models import audit_log

    Base.metadata.create_all(bind=engine)