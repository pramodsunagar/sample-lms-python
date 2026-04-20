from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.user import User, UserProfile
from app.routes.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/profile")
async def profile_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    return templates.TemplateResponse(
        "profile.html", {"request": request, "user": current_user, "profile": profile}
    )


@router.post("/profile")
async def update_profile(
    request: Request,
    current_role: str = Form(""),
    skills_owned: str = Form(""),
    learning_goal: str = Form(""),
    experience_level: str = Form("beginner"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    profile.current_role = current_role
    profile.skills_owned = skills_owned
    profile.learning_goal = learning_goal
    profile.experience_level = experience_level
    db.commit()
    return RedirectResponse("/dashboard", status_code=302)
