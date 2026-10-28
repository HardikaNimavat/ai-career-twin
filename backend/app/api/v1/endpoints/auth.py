import uuid
import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_password_hash, verify_password, create_access_token
from backend.app.models.user import User
from pydantic import BaseModel
from backend.app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from backend.app.api.deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegisterRequest, response: Response, db: Session = Depends(get_db)):
    email_clean = payload.email.lower().strip()
    existing_user = db.query(User).filter(User.email == email_clean).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )

    if payload.username:
        existing_username = db.query(User).filter(User.username == payload.username.strip()).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this username already exists."
            )

    hashed_pw = get_password_hash(payload.password)
    new_user = User(
        public_id=str(uuid.uuid4()),
        email=email_clean,
        username=payload.username.strip() if payload.username else None,
        hashed_password=hashed_pw,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": str(new_user.id)})
    
    # Also set httpOnly cookie for secure browser storage
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # Set to True in production with HTTPS
        max_age=3600
    )

    logger.info("Registered new user #%s (%s)", new_user.id, new_user.email)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )

@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLoginRequest, response: Response, db: Session = Depends(get_db)):
    login_id = payload.email.strip()
    user = db.query(User).filter(
        (User.email == login_id.lower()) | (User.username == login_id)
    ).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive."
        )

    token = create_access_token({"sub": str(user.id)})

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=3600
    )

    logger.info("User #%s (%s) logged in", user.id, user.email)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

class GitHubSessionPayload(BaseModel):
    github_username: str

@router.post("/github-session", response_model=TokenResponse)
def github_session_login(
    payload: GitHubSessionPayload,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Direct GitHub account entry:
    Verifies that the GitHub user is valid, then establishes an authenticated session
    without requiring any traditional email/password registration or login.
    """
    from backend.app.services.github_analyzer import github_analyzer
    
    clean_handle = payload.github_username.strip().lstrip("@")
    if not clean_handle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub username cannot be empty."
        )

    # Verify that the GitHub user exists
    verify_res = github_analyzer.verify_user(clean_handle)
    if not verify_res.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=verify_res.get("error", f"GitHub user '{clean_handle}' does not exist.")
        )

    canonical_username = verify_res.get("username", clean_handle)
    email_for_user = f"{canonical_username.lower()}@github.career-twin.local"

    # Find existing user or create a new user profile
    user = db.query(User).filter(
        (User.username == canonical_username) | (User.email == email_for_user)
    ).first()

    if not user:
        user = User(
            public_id=str(uuid.uuid4()),
            email=email_for_user,
            username=canonical_username,
            hashed_password=get_password_hash("github_sso_nopassword_session"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": str(user.id)}, expires_delta=timedelta(days=7))

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=86400 * 7
    )

    logger.info("GitHub session established for user #%s (@%s)", user.id, canonical_username)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.post("/logout")
def logout_user(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out."}

