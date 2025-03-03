from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from .models import Base
from .database import engine
from .routers import auth, todos, admin, users
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()
Base.metadata.create_all(bind=engine)

# Get absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "TodoApp", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "TodoApp", "static")
IMAGES_DIR = os.path.join(BASE_DIR, "TodoApp", "static", "images")

# Debug prints
print("Base directory:", BASE_DIR)
print("Templates directory:", TEMPLATES_DIR)
print("Does templates exist?", os.path.exists(TEMPLATES_DIR))
if os.path.exists(TEMPLATES_DIR):
    print("Templates contents:", os.listdir(TEMPLATES_DIR))

# Mount static directories
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

# Set templates directory
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/")
def test(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/healthy")
def healthcheck():
    return {"status": "healthy"}

app.include_router(todos.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)

