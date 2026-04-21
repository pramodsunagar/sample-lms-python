from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from app.config import SECRET_KEY
from app.database.db import init_db, get_db
from app.models.user import UserProfile
from app.routes import auth, profile, learning
from app.services.azure_training import get_relevant_events


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI Learning Experience Platform", lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(learning.router)


@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    skills_owned = ""
    if user_id:
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if user_profile and user_profile.skills_owned:
            skills_owned = user_profile.skills_owned
    azure_events = get_relevant_events(skills_owned)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user_id": user_id, "azure_events": azure_events},
    )
