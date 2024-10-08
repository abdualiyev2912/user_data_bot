import os
from datetime import timedelta, datetime
from utils.db import SessionLocal
from models import User, UserRole
from typing import Optional, Dict, List
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer 
from fastapi import HTTPException, status, Depends
from jose import jwt, JWTError
from dotenv import load_dotenv


load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/users/token')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def create_user(user_data: Dict) -> User:
    session = SessionLocal()
    try:
        db_user = session.query(User).filter(User.id == user_data["id"]).first()
        if db_user is None:
            new_user = User(
                id=user_data["id"],
                fish=user_data["fish"],
                phone=user_data["phone"]
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            return new_user
        return db_user
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

async def get_user(user_id: int) -> Optional[User]:
    session = SessionLocal()
    try:
        return session.query(User).filter(User.id == user_id).first()
    finally:
        session.close()

async def get_user_by_phone(phone_number: int) -> Optional[User]:
    session = SessionLocal()
    try:
        return session.query(User).filter(User.phone == phone_number).first()
    finally:
        session.close()

async def get_users(skip: int = 0, limit: int = 10) -> List[User]:
    session = SessionLocal()
    try:
        return session.query(User).offset(skip).limit(10).all()
    finally:
        session.close()

async def get_admin_user() -> Optional[User]:
    session = SessionLocal()
    try:
        return session.query(User).filter(User.role == UserRole.ADMIN).first()
    finally:
        session.close()

async def update_user_role(user_id: int) -> Optional[User]:
    session = SessionLocal()
    try:
        db_user = session.query(User).filter(User.id == user_id).first()
        if db_user:
            if db_user.role == UserRole.CLIENT:
                db_user.role = UserRole.STAFF
            else:
                db_user.role = UserRole.CLIENT
            session.commit()
            session.refresh(db_user)
            return db_user
        return None
    except Exception as e:
        session.rollback()
    finally:
        session.close()

async def update_user(user_id: int, update_data: Dict) -> Optional[User]:
    session = SessionLocal()
    try:
        db_user = session.query(User).filter(User.id == user_id).first()
        if db_user:
            for key, value in update_data.items():
                setattr(db_user, key, value)
            session.commit()
            session.refresh(db_user)
            return db_user
        return None
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

async def delete_user(user_id: int) -> bool:
    session = SessionLocal()
    try:
        db_user = session.query(User).filter(User.id == user_id).first()
        if db_user:
            session.delete(db_user)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()


async def authenticate_user(user_data):
    db_user = await get_admin_user()

    if not verify_password(user_data.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telefon raqam yoki parol xato!",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return db_user

async def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expires_delta = timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')))
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))
    return encoded_jwt

async def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expires_delta = timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")))
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))
    return encoded_jwt

async def verify_token(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])
        phone_number: str = payload.get("sub")
        if phone_number is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token yaroqsiz!")
        return phone_number
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token yaroqsiz!")

async def get_current_user(phone_number: str = Depends(verify_token)) -> User:
    user = await get_user_by_phone(phone_number)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hisob ma'lumotlarini tekshirib bo'lmadi!",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sizda bunday huquq yo'q!",
        )
    return current_user