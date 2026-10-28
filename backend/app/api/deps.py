from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.core.database import get_db
from backend.app.core.security import decode_access_token
from backend.app.models.user import User

security_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    request: Request,
    token_auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    token: Optional[str] = None
    if token_auth and token_auth.credentials:
        token = token_auth.credentials
    elif "access_token" in request.cookies:
        token = request.cookies.get("access_token")

    if token:
        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")
            if user_id:
                user = db.query(User).filter(User.id == int(user_id)).first()
                if user and user.is_active:
                    return user
        except Exception:
            pass

    # Check for X-GitHub-Username header for zero-friction identity
    gh_header = request.headers.get("X-GitHub-Username") or request.headers.get("x-github-username")
    if gh_header:
        gh_handle = gh_header.strip().lstrip("@")
        email_for_user = f"{gh_handle.lower()}@github.career-twin.local"

        user = db.query(User).filter(
            (User.username == gh_handle) | (User.email == email_for_user)
        ).first()

        if not user:
            from backend.app.core.security import get_password_hash
            import uuid
            user = User(
                public_id=str(uuid.uuid4()),
                email=email_for_user,
                username=gh_handle,
                hashed_password=get_password_hash("github_auto_identity"),
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Please connect with your GitHub account.",
        headers={"WWW-Authenticate": "Bearer"},
    )
