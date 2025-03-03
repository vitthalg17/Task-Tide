from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:ep5vSQFVyxyqOhnh@liberally-current-butterfly.data-1.apse1.tembo.io:5432/postgres"

engine=create_engine(SQLALCHEMY_DATABASE_URL)

Sessionlocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()
