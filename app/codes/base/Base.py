from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.constants import NEWRL_DB

engine = create_engine('sqlite:///'+NEWRL_DB)
session = sessionmaker(bind=engine)
print("Base is loading")

Base = declarative_base()

def get_session():
    return session