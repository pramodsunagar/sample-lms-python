import json
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.user import User, UserProfile
from app.models.learning import SavedPath, CourseProgress, PathRemovalLog
from app.routes.auth import get_current_user
from app.services import ai_service, aggregator

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/generate")
async def generate_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    return templates.TemplateResponse(
        "generate.html", {"request": request, "user": current_user, "profile": profile}
    )


@router.post("/generate")
async def generate_path(
    request: Request,
    role: str = Form(...),
    target_skill: str = Form(...),
    level: str = Form("beginner"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        return RedirectResponse("/login", status_code=302)

    # Step 1: AI skill gap analysis
    analysis = ai_service.analyze_skill_gap(role, target_skill)
    skill_level = analysis.get("skill_level", level)
    search_terms = analysis.get("search_terms", [target_skill])
    ms_roles = analysis.get("ms_learn_roles", ["developer"])
    ms_products = analysis.get("ms_learn_products", ["azure"])
    rationale = analysis.get("rationale", "")
    learning_sequence = analysis.get("learning_sequence", [])

    # Step 2: Aggregate courses from all sources
    courses = await aggregator.aggregate(
        roles=ms_roles,
        levels=[skill_level],
        products=ms_products,
        search_terms=search_terms,
    )

    # Step 3: AI ranking
    ranked = ai_service.rank_and_curate(role, target_skill, skill_level, courses)

    # Step 4: Generate weekly sequence
    weekly_plan = ai_service.generate_learning_sequence(target_skill, ranked)

    # Build a URL -> course map for template rendering
    course_map = {c.get("url"): c for c in ranked}

    # Normalize weekly_plan: replace AI-hallucinated URLs with real ones
    url_set = set(course_map.keys())
    has_valid = any(
        any(u in url_set for u in week.get("course_urls", []))
        for week in weekly_plan
    )
    if not has_valid or not weekly_plan:
        # AI returned bad/hallucinated URLs � distribute ranked courses evenly across 3 weeks
        chunk = max(1, len(ranked) // 3)
        weekly_plan = [
            {
                "week": f"Week {i * chunk + 1}\u2013{min((i + 1) * chunk, len(ranked))}",
                "theme": target_skill,
                "course_urls": [c["url"] for c in ranked[i * chunk:(i + 1) * chunk]],
            }
            for i in range(3)
            if ranked[i * chunk:(i + 1) * chunk]
        ]

    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "user": current_user,
            "role": role,
            "target_skill": target_skill,
            "skill_level": skill_level,
            "rationale": rationale,
            "learning_sequence": learning_sequence,
            "courses": ranked,
            "weekly_plan": weekly_plan,
            "course_map": course_map,
            "courses_json": json.dumps(ranked),
        },
    )


@router.post("/save")
async def save_path(
    request: Request,
    role: str = Form(...),
    target_skill: str = Form(...),
    courses_json: str = Form(...),
    ai_rationale: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    courses = json.loads(courses_json)
    path = SavedPath(
        user_id=current_user.id,
        title=f"{target_skill} for {role}",
        role=role,
        target_skill=target_skill,
        courses=courses,
        ai_rationale=ai_rationale,
    )
    db.add(path)
    db.commit()
    return RedirectResponse("/dashboard", status_code=302)


@router.get("/dashboard")
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    paths = (
        db.query(SavedPath)
        .filter(SavedPath.user_id == current_user.id)
        .order_by(SavedPath.created_at.desc())
        .all()
    )
    progress_records = (
        db.query(CourseProgress)
        .filter(CourseProgress.user_id == current_user.id)
        .all()
    )
    progress_map = {p.course_url: p.status for p in progress_records}
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": current_user,
            "paths": paths,
            "progress_map": progress_map,
        },
    )


@router.post("/progress")
async def update_progress(
    request: Request,
    course_url: str = Form(...),
    course_title: str = Form(""),
    saved_path_id: int = Form(None),
    status: str = Form("in_progress"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    record = (
        db.query(CourseProgress)
        .filter(
            CourseProgress.user_id == current_user.id,
            CourseProgress.course_url == course_url,
        )
        .first()
    )
    if record:
        record.status = status
    else:
        record = CourseProgress(
            user_id=current_user.id,
            saved_path_id=saved_path_id,
            course_url=course_url,
            course_title=course_title,
            status=status,
        )
        db.add(record)
    db.commit()
    return RedirectResponse("/dashboard", status_code=302)


@router.post("/remove-path")
async def remove_path(
    request: Request,
    path_id: int = Form(...),
    removal_reason: str = Form(""),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user:
        return RedirectResponse("/login", status_code=302)

    path = db.query(SavedPath).filter(
        SavedPath.id == path_id,
        SavedPath.user_id == current_user.id
    ).first()

    if path:
        # Log the removal
        log = PathRemovalLog(
            user_id=current_user.id,
            path_title=path.title,
            removal_reason=removal_reason.strip() or "No reason provided",
        )
        db.add(log)
        # Delete associated progress records
        db.query(CourseProgress).filter(CourseProgress.saved_path_id == path_id).delete()
        db.delete(path)
        db.commit()

    return RedirectResponse("/dashboard", status_code=303)


@router.get("/remove-path")
async def remove_path_get(
    request: Request,
    current_user=Depends(get_current_user),
):
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    return RedirectResponse("/dashboard", status_code=302)
