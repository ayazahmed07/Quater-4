from fastapi import FastAPI, Depends
import os
from sqlmodel import SQLModel, create_engine
from dotenv import load_dotenv
from sqlmodel import Field
from contextlib import asynccontextmanager
from sqlmodel import Session
from typing import Annotated 
import psycopg2


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True) #show logs echo true

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    age: int


@asynccontextmanager
async def table_creation_fucntion(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    print("Tables created successfully.")
    yield #pause here and wait for shutdown
    # Optionally, you can add teardown logic here if needed
    print("Application shutdown.")


app = FastAPI(lifespan=table_creation_fucntion) #generate tables on startup

# Dependency to get a session
def get_session():
    with Session(engine) as session:
        yield session


@app.get("/")
def read_root():
    return {"Hello": "World"}   


@app.post("/users/")
def create_user(user: User, session: Annotated [Session, Depends(get_session)]):
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User created successfully", "user": user}
  

#make it with so dont need to close session manually


    

