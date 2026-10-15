from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """One-way hash. Salt is generated automatically and stored inside the result."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Re-hash the attempt with the stored salt and compare. Used in Gate 7."""
    return pwd_context.verify(plain, hashed)