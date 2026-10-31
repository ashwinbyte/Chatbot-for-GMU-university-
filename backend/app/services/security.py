import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

# .env lives at the project root, this file is 3 folders deeper
load_dotenv(Path(__file__).resolve().parents[3] / ".env")

JWT_SECRET = os.environ["JWT_SECRET"]
ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain):
    return pwd_context.hash(plain)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id):
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(user_id),  
            "iat": now,
            "exp": now + timedelta(hours=TOKEN_EXPIRY_HOURS),
        },
        JWT_SECRET,
        algorithm=ALGORITHM,
    )

def read_user_id(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None