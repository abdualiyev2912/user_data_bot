from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from utils.db import get_db
from typing import List
from schemas import user_schemas
from crud import user_crud
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.get("/", response_model=List[user_schemas.User], dependencies=[Depends(user_crud.get_current_admin_user)])
async def read_users(skip: int = 0, limit: int = 10):
    return await user_crud.get_users(skip, limit)

@router.post("/token", response_model=user_schemas.Token)
async def login_for_access_token(user_data: OAuth2PasswordRequestForm = Depends()):
    db_user = await user_crud.authenticate_user(user_schemas.UserSignIn(phone=user_data.username,password=user_data.password))
    access_token = await user_crud.create_access_token({"sub": db_user.phone})
    refresh_token = await user_crud.create_refresh_token({"sub": db_user.phone})
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }

@router.get("/verify-token/")
async def verify_user_token(current_user: user_schemas.User = Depends(user_crud.get_admin_user)):
    return {
        'success': True,
        "message": "Token yaroqli!",
        "data": current_user
    }