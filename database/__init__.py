import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base


engine = create_engine(f"sqlite:///{os.path.expanduser('~/catch/catch_database.db')}", echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

print(session)

print("Database connection established.")
