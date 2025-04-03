from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from models import Base
from database import engine
from routers import auth, todos, admin, users
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()
Base.metadata.create_all(bind=engine)

# Get the current directory
current_dir = os.path.dirname(os.path.realpath(__file__))

# Mount static directories
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")
app.mount("/images", StaticFiles(directory=os.path.join(current_dir, "static/images")), name="images")

# Set templates directory
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

@app.get("/")
def test(request: Request):
    return templates.TemplateResponse("home.html",{"request":request})

@app.get("/healthy")
def healthcheck():
    return {"status": "healthy"}

app.include_router(todos.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)

@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    return templates.TemplateResponse("404.html", {"request": request})

# Disable FastAPI default exception handler to prevent alert popups
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc):
    return {"status": "error", "detail": str(exc)}

