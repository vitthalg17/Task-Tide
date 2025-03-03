from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from .models import Base
from .database import engine
from .routers import auth, todos, admin, users
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()
Base.metadata.create_all(bind=engine)

# Get the deployment directory
DEPLOY_DIR = "/opt/render/project/src"
APP_DIR = os.path.join(DEPLOY_DIR, "TodoApp")

# Debug prints
print("Current working directory:", os.getcwd())
print("Contents of current directory:", os.listdir())
print("Contents of TodoApp directory:", os.listdir(APP_DIR))

# Mount static directories
app.mount("/static", StaticFiles(directory=os.path.join(APP_DIR, "static")), name="static")
app.mount("/images", StaticFiles(directory=os.path.join(APP_DIR, "static/images")), name="images")

# Set templates directory
templates = Jinja2Templates(directory=os.path.join(APP_DIR, "templates"))

@app.get("/")
def test(request: Request):
    template_dir = os.path.join(APP_DIR, "templates")
    print(f"Looking for templates in: {template_dir}")
    print(f"Templates directory exists: {os.path.exists(template_dir)}")
    if os.path.exists(template_dir):
        print("Templates directory contents:", os.listdir(template_dir))
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/healthy")
def healthcheck():
    return {"status": "healthy"}

app.include_router(todos.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)

