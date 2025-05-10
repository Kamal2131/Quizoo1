from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate
from auth import get_password_hash  # Assumes this hashes plaintext passwords

# Retrieve a user by username
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# Create a new user with hashed password
def create_user(db: Session, user: UserCreate):
    hashed_pw = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
