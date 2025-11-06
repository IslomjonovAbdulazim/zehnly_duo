from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
from .config import settings

security = HTTPBearer()


class AdminLogin(BaseModel):
    email: str
    password: str


class AdminToken(BaseModel):
    access_token: str
    token_type: str


def create_admin_token(email: str) -> str:
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "admin"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        token_type = payload.get("type")
        
        if email != settings.SUPER_ADMIN_EMAIL or token_type != "admin":
            raise HTTPException(status_code=403, detail="Invalid admin token")
        
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def login_admin(login_data: AdminLogin) -> AdminToken:
    if (login_data.email != settings.SUPER_ADMIN_EMAIL or 
        login_data.password != settings.SUPER_ADMIN_PASSWORD):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_admin_token(login_data.email)
    return AdminToken(access_token=token, token_type="bearer")