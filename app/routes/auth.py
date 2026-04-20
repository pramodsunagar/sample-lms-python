import bcrypt
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})


@router.post("/register")
async def register(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": "Email already registered."}
        )
    user = User(
        username=full_name,
        email=email,
        hashed_password=_hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    request.session["user_id"] = user.id
    return RedirectResponse("/profile", status_code=302)


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not _verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Invalid email or password."}
        )
    request.session["user_id"] = user.id
    return RedirectResponse("/dashboard", status_code=302)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)
