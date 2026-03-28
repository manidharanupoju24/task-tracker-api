from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from app.auth import bearer_scheme
from app.limiter import limiter
from app.supabase_client import supabase_admin

router = APIRouter(prefix="/auth", tags=["auth"])


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/signup", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def sign_up(request: Request, body: SignUpRequest):
    response = supabase_admin.auth.sign_up({
        "email": body.email,
        "password": body.password,
        "options": {"data": {"display_name": body.display_name}},
    })
    if response.user is None:
        raise HTTPException(status_code=400, detail="Sign up failed")
    return {"message": "Account created. Please check your email to confirm."}


@router.post("/signin")
@limiter.limit("5/minute")
def sign_in(request: Request, body: SignInRequest):
    response = supabase_admin.auth.sign_in_with_password({
        "email": body.email,
        "password": body.password,
    })
    if response.session is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {
        "access_token": response.session.access_token,
        "token_type": "bearer",
    }


@router.post("/signout")
def sign_out(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    supabase_admin.auth.admin.sign_out(credentials.credentials)
    return {"message": "Signed out successfully"}
