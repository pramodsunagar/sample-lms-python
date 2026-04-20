from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from app.config import SECRET_KEY
from app.database.db import init_db
from app.routes import auth, profile, learning


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
async def home(request: Request):
    user_id = request.session.get("user_id")
    return templates.TemplateResponse("index.html", {"request": request, "user_id": user_id})
