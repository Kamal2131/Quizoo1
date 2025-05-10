from fastapi import FastAPI, Request, Form, Depends, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base
from schemas import UserCreate
from crud import get_user_by_username, create_user
from auth import verify_password, create_access_token, get_current_user_from_token
from quiz_router import router as quiz_router

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ======= ROUTES =======

app.include_router(quiz_router)

def get_template_context(request: Request):
    token = request.cookies.get("token")
    username = get_current_user_from_token(token) if token else None
    return {
        "request": request,
        "logged_in": bool(username),
        "username": username
    }

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", get_template_context(request))

@app.get("/register", response_class=HTMLResponse)
def show_register(request: Request):
    context = get_template_context(request)
    if context["logged_in"]:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("register.html", context)

@app.get("/login", response_class=HTMLResponse)
def show_login(request: Request):
    context = get_template_context(request)
    if context["logged_in"]:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    
    # Get message from query parameters
    context["msg"] = request.query_params.get("msg")
    return templates.TemplateResponse("login.html", context)

@app.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    if get_user_by_username(db, username):
        return templates.TemplateResponse("register.html", {
            **get_template_context(request),
            "msg": "Username already exists!"
        })

    user = UserCreate(username=username, email=email, password=password)
    create_user(db, user)

    return templates.TemplateResponse("login.html", {
        **get_template_context(request),
        "msg": "Registration successful! Please login."
    })

@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            **get_template_context(request),
            "msg": "Invalid credentials!"
        })

    token = create_access_token(data={"sub": username})
    response = templates.TemplateResponse("dashboard.html", {
        **get_template_context(request),
        "username": username,
        "logged_in": True,
        "welcome_message": True  # Add this flag
    })
    response.set_cookie(key="token", value=token, httponly=True)
    return response

@app.get("/logout")
def logout():
    response = RedirectResponse(
        url="/login?msg=Logged+out+successfully",  # Add query parameter
        status_code=status.HTTP_302_FOUND
    )
    response.delete_cookie("token")
    return response

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    context = get_template_context(request)
    if not context["logged_in"]:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    context["welcome_message"] = True  # Add this line
    return templates.TemplateResponse("dashboard.html", context)