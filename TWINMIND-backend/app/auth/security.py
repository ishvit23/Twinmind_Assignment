from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# Get secret from env
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Bcrypt context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MAX_BCRYPT_LENGTH = 72   # bcrypt will ignore anything after 72 bytes


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def hash_password(password: str) -> str:
    """
    bcrypt only hashes the first 72 bytes.
    We truncate safely before hashing to avoid backend errors.
    """
    if password is None:
        password = ""
    password = password[:MAX_BCRYPT_LENGTH]  # 🔥 hard truncate
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    MUST truncate the password here also, because user's input
    might exceed 72 characters → bcrypt would ignore rest.
    """
    if plain_password is None:
        plain_password = ""
    plain_password = plain_password[:MAX_BCRYPT_LENGTH]  # 🔥 truncate
    return pwd_context.verify(plain_password, hashed_password)
