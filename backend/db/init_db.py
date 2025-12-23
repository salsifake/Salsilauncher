from sqlmodel import SQLModel
from .engine import engine

def init_db():
    SQLModel.metadata.create_all(engine)
