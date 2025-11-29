from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

from app.database.connection import get_db
from app.models.user import User
from app.auth.security import hash_password, verify_password, create_access_token

logger = logging.getLogger(__name__)
router = APIRouter()

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/auth/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        # Validate inputs
        if len(request.password) > 72:
            raise HTTPException(status_code=400, detail="Password too long (max 72 characters)")
        if len(request.username) < 3:
            raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
        if len(request.email) < 5:
            raise HTTPException(status_code=400, detail="Invalid email")
        
        # Check if user exists
        existing = db.query(User).filter(User.username == request.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Create user
        user = User(
            username=request.username,
            email=request.email,
            hashed_password=hash_password(request.password[:72])  # Limit to 72 chars
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return {
            "status": "success",
            "message": "User registered successfully",
            "user_id": user.id,
            "username": user.username
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        # Find user
        user = db.query(User).filter(User.username == request.username).first()
        if not user or not verify_password(request.password[:72], user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create token
        token = create_access_token({"sub": user.id, "username": user.username})
        
        return {
            "status": "success",
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))