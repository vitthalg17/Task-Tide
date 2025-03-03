from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from .models import Base
from .database import engine
from .routers import auth, todos, admin, users
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()
Base.metadata.create_all(bind=engine)

# Print current directory and contents for debugging
print("Current directory:", os.getcwd())
print("Directory contents:", os.listdir())

# Mount static directories
app.mount("/static", StaticFiles(directory="TodoApp/static"), name="static")
app.mount("/images", StaticFiles(directory="TodoApp/static/images"), name="images")

# Set templates directory
templates = Jinja2Templates(directory="TodoApp/templates")

@app.get("/")
def test(request: Request):
    # Print template directory contents for debugging
    template_dir = "TodoApp/templates"
    print(f"Template directory: {template_dir}")
    if os.path.exists(template_dir):
        print("Template directory contents:", os.listdir(template_dir))
    else:
        print("Template directory not found!")
    
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/healthy")
def healthcheck():
    return {"status": "healthy"}

app.include_router(todos.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)

