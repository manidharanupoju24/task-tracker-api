from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.supabase_client import supabase_admin

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    Validates the Supabase JWT by calling Supabase's own auth.get_user().
    Works with both RS256 (new JWT signing keys) and HS256 (legacy secret).
    """
    token = credentials.credentials
    try:
        response = supabase_admin.auth.get_user(token)
        if response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        metadata = response.user.user_metadata or {}
        return {
            "sub": response.user.id,
            "email": response.user.email,
            "display_name": metadata.get("display_name") or response.user.email.split("@")[0],
        }
    except Exception as e:
        print(f"Auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def get_user_id(payload: dict = Depends(get_current_user)) -> str:
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not identify user",
        )
    return user_id
