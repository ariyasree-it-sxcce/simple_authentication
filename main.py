from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker

# ---------------- FASTAPI APP ----------------

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key",
    max_age=300 # session expires after 5 minutes
)

# ---------------- DATABASE CONFIG (MySQL) ----------------

DATABASE_URL = "mysql+pymysql://root:ariya123@localhost:3306/simple_auth_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    username = Column(String(100), primary_key=True)
    password = Column(String(100))

Base.metadata.create_all(engine)

# ---------------- REGISTER ----------------

@app.post("/register")
async def register(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    db = SessionLocal()

    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        db.close()
        return JSONResponse(
            status_code=400,
            content={"message": "User already exists"}
        )

    new_user = User(username=username, password=password)
    db.add(new_user)
    db.commit()
    db.close()

    return {"message": "User registered successfully"}

# ---------------- LOGIN ----------------

@app.post("/login")
async def login(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    db = SessionLocal()

    user = db.query(User).filter(
        User.username == username,
        User.password == password
    ).first()

    db.close()

    if not user:
        return JSONResponse(
            status_code=401,
            content={"message": "Wrong username or password"}
        )

    request.session["user"] = username
    return {"message": "Login success"}

# ---------------- HOME (Protected) ----------------

@app.get("/home")
def home(request: Request):
    if "user" not in request.session:
        return JSONResponse(
            status_code=401,
            content={"message": "Please login"}
        )

    return {"message": f"Welcome {request.session['user']}"}

# ---------------- LOGOUT ----------------

@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out"}
