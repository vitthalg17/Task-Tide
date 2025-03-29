from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from pydantic import BaseModel, Field
from typing import Annotated
from starlette import status
from sqlalchemy.orm import Session
from models import Todos
from database import Sessionlocal
from .auth import get_current_user, SECRET_KEY, ALGORITHM
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from jose import JWTError, jwt

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}},
)


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(ge=1, le=5)
    complete: bool = Field(default=False)


def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response


### Pages ###
@router.get("/todo-page", status_code=status.HTTP_200_OK)
async def render_todos_page(request: Request, db: db_dependency):
    try:
        token = request.cookies.get("access_token")
        if not token:
            print("No token found in cookies")
            return redirect_to_login()
            
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("id")
            if not user_id:
                print("No user_id in token payload")
                return redirect_to_login()
            
            # Convert user_id to int if it's a string
            if isinstance(user_id, str):
                user_id = int(user_id)
                
            todos = db.query(Todos).filter(Todos.owner_id == user_id).all()
            print(f"Found {len(todos)} todos for user {user_id}")
            return templates.TemplateResponse("todos.html", {"request": request, "todos": todos})
            
        except JWTError as e:
            print(f"JWT decode error: {str(e)}")
            return redirect_to_login()
        except ValueError as e:
            print(f"Value error: {str(e)}")
            return redirect_to_login()
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return redirect_to_login()
    
@router.get("/add-todo-page", status_code=status.HTTP_200_OK)
async def render_add_todo_page(request: Request):
    try:
        token = request.cookies.get("access_token")
        if not token:
            print("No token found in cookies")
            return redirect_to_login()
            
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("id")
            if not user_id:
                print("No user_id in token payload")
                return redirect_to_login()
                
            return templates.TemplateResponse("add-todo.html", {"request": request})
            
        except JWTError as e:
            print(f"JWT decode error: {str(e)}")
            return redirect_to_login()
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return redirect_to_login()

@router.get("/edit-todo-page/{todo_id}", status_code=status.HTTP_200_OK)
async def render_edit_todo_page(request: Request, db: db_dependency, todo_id: int = Path(gt=0)):
    try:
        token = request.cookies.get("access_token")
        if not token:
            print("No token found in cookies")
            return redirect_to_login()
        
        todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

        return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo_model})
    except:
        return redirect_to_login()
            
### EndPoints ###
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()

@router.get('/todo/{todo_id}', status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")

@router.post('/todo', status_code=status.HTTP_201_CREATED)
async def create_todo(request: Request, todo_request: TodoRequest, db: db_dependency):
    try:
        # Try to get token from cookie first
        token = request.cookies.get("access_token")
        if not token:
            # If no cookie, check Authorization header
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
            else:
                raise HTTPException(status_code=401, detail="Authentication Failed")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("id")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")

            todo_model = Todos(**todo_request.dict(), owner_id=user_id)
            db.add(todo_model)
            db.commit()
            
            # Return a simple success response
            return {"message": "Todo created successfully"}

        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(todo_request: TodoRequest, user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        todo_model.title = todo_request.title
        todo_model.description = todo_request.description
        todo_model.priority = todo_request.priority
        todo_model.complete = todo_request.complete
        db.commit()
        return
    raise HTTPException(status_code=404, detail="Todo not found")

@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).delete()
    db.commit()
    