from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, EmailStr, Field
from uuid import uuid4
from app.auth.security import hash_password, verify_password, issue_token, verify_token
from app.db.user_store import user_store

router = APIRouter(prefix="/auth", tags=["auth"])

class Signup(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)
    name: str = Field(min_length=1, max_length=120)

class Login(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)

@router.post("/signup", status_code=201)
def signup(payload: Signup):
    email = payload.email.lower()
    if user_store.find_by_email(email):
        raise HTTPException(409, "Account already exists")
    user = {
        "id": str(uuid4()),
        "email": email,
        "name": payload.name.strip(),
        "password_hash": hash_password(payload.password),
        "role": "admin",
    }
    user_store.create(user)
    return {"user": {"id": user["id"], "email": user["email"], "name": user["name"], "role": user["role"]},
            "token": issue_token(user["id"])}

@router.post("/login")
def login(payload: Login):
    user = user_store.find_by_email(payload.email.lower())
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(401, "Invalid credentials")
    return {"user": {"id": user["id"], "email": user["email"], "name": user["name"], "role": user["role"]},
            "token": issue_token(user["id"])}

@router.get("/me")
def me(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Authentication required")
    user_id = verify_token(authorization[7:])
    user = user_store.find(user_id) if user_id else None
    if not user:
        raise HTTPException(401, "Invalid or expired token")
    return {"id": user["id"], "email": user["email"], "name": user["name"], "role": user["role"]}
