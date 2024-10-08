from sqlalchemy.orm import Session
from models import *
from crud import user_crud
from utils.db import SessionLocal, engine

def create_initial_users(db: Session):
    admin = User(
        id=6956977079,
        fish="Admin",
        phone="+998901234567",
        password=user_crud.get_password_hash("1"),
        role=UserRole.ADMIN,
        shaxs="jismmoniy"
    )
    db.add(admin)
    db.commit()

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    create_initial_users(db)
    db.close()