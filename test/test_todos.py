from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from TodoApp.database import Base, get_db
from TodoApp.main import app
from TodoApp.routers.todos import get_current_user
from fastapi.testclient import TestClient
from fastapi import status

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:123@localhost/test_todoapp"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {'username': 'testuser', 'id': 1, 'user_role': 'admin'}

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

def test_read_all_authenticated():
    response = client.get("/todos/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []