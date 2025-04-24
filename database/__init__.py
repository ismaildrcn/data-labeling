import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

engine = create_engine(f"sqlite:///{os.path.expanduser('~/catch/catch_database.db')}", echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

print(session)

print("Database connection established.")
