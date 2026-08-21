from sqlalchemy.orm import Session

from app.models.user import User
from app.security import hash_password, verify_password


def get_user_by_username(
    db: Session,
    username: str
):
    """
    Find a user using username.
    """

    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


def get_user_by_email(
    db: Session,
    email: str
):
    """
    Find a user using email.
    """

    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    role: str = "CUSTOMER"
):
    """
    Create a new user.
    """

    # Check username
    if get_user_by_username(db, username):
        raise ValueError(
            "Username already exists"
        )

    # Check email
    if get_user_by_email(db, email):
        raise ValueError(
            "Email already registered"
        )

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    username: str,
    password: str
):
    """
    Verify username and password.
    """

    user = get_user_by_username(
        db,
        username
    )

    if not user:
        return None

    if not user.is_active:
        return None

    if not verify_password(
        password,
        user.password_hash
    ):
        return None

    return user