from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services.security import read_user_id

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
):
    not_allowed = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if creds is None:
        raise not_allowed

    user_id = read_user_id(creds.credentials)
    if user_id is None:
        raise not_allowed

    # token can outlive the account, so make sure they still exist
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise not_allowed

    return user