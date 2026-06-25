from pathlib import Path
from time import time
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .config import get_settings
from .database import Base, engine, get_db
from .deps import get_current_user, require_admin
from .models import ContactMessage, NewsletterSubscriber, User
from .schemas import (
    ContactCreate,
    ContactOut,
    MessageOut,
    NewsletterCreate,
    TokenOut,
    UserCreate,
    UserLogin,
    UserOut,
)
from .security import create_access_token, get_password_hash, verify_password


settings = get_settings()
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title=settings.app_name, version="1.0.0")

if settings.env == "production" and settings.secret_key == "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY":
    raise RuntimeError("Change SECRET_KEY before production deployment.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.hosts + ["*"] if settings.env == "development" else settings.hosts)

rate_store: dict[str, list[float]] = {}
SENSITIVE_PATHS = {"/api/auth/login", "/api/auth/register", "/api/contact", "/api/newsletter"}


@app.middleware("http")
async def security_and_rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    key = f"{client_ip}:{request.url.path}"

    if request.url.path in SENSITIVE_PATHS:
        now = time()
        window_start = now - 60
        attempts = [t for t in rate_store.get(key, []) if t > window_start]
        if len(attempts) >= 10:
            return JSONResponse(status_code=429, content={"detail": "Too many requests. Try again later."})
        attempts.append(now)
        rate_store[key] = attempts

    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
   # response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    if settings.env == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")


@app.get("/", include_in_schema=False)
def homepage():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name}


@app.post("/api/auth/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user_count = db.query(User).count()
    role = "admin" if user_count == 0 else "user"

    user = User(
        full_name=payload.full_name.strip(),
        email=payload.email.lower(),
        hashed_password=get_password_hash(payload.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.email, extra={"role": user.role})
    return TokenOut(access_token=token, user=user)


@app.post("/api/auth/login", response_model=TokenOut)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    token = create_access_token(subject=user.email, extra={"role": user.role})
    return TokenOut(access_token=token, user=user)


@app.get("/api/auth/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/api/contact", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def create_contact(payload: ContactCreate, db: Session = Depends(get_db)):
    item = ContactMessage(
        name=payload.name.strip(),
        email=payload.email.lower(),
        message=payload.message.strip(),
    )
    db.add(item)
    db.commit()
    return MessageOut(message="Message received successfully")


@app.post("/api/newsletter", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def subscribe(payload: NewsletterCreate, db: Session = Depends(get_db)):
    subscriber = NewsletterSubscriber(email=payload.email.lower())
    db.add(subscriber)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return MessageOut(message="You are already subscribed")
    return MessageOut(message="Subscribed successfully")


@app.get("/api/admin/messages", response_model=list[ContactOut])
def list_messages(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(ContactMessage).order_by(ContactMessage.id.desc()).limit(100).all()
