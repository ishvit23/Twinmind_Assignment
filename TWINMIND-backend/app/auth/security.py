from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# ============================================================
# JWT CONFIG
# ============================================================
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ============================================================
# BCRYPT CONFIG
# ============================================================
# Use ONLY bcrypt (not py-bcrypt). Passlib’s CryptContext will load correct backend.
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

# bcrypt ignores everything after 72 bytes → we manually truncate to avoid errors
MAX_BCRYPT_LENGTH = 72


# ============================================================
# JWT CREATION & VALIDATION
# ============================================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token with expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str) -> Optional[dict]:
    """Decode JWT token and return payload or None if invalid."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# ============================================================
# PASSWORD HASHING & VERIFYING WITH SAFE TRUNCATION
# ============================================================
def hash_password(password: str) -> str:
    """
    bcrypt ONLY uses the first 72 bytes.
    We safely truncate to prevent bcrypt backend errors.
    """
    if not password:
        password = ""

    # 🔥 hard truncate
    safe_password = password[:MAX_BCRYPT_LENGTH]

    return pwd_context.hash(safe_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Truncate password BEFORE verifying, otherwise bcrypt will mismatch.
    """
    if not plain_password:
        plain_password = ""

    # 🔥 same truncate logic
    safe_password = plain_password[:MAX_BCRYPT_LENGTH]

    return pwd_context.verify(safe_password, hashed_password)
