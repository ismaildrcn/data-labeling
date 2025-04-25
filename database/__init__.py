import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from database.models.image.model import Image
from database.models.label.model import Label 
from database.models.annotation.model import Annotation
from database.models.setting.model import Setting

Base = declarative_base()

engine = create_engine(f"sqlite:///{os.path.expanduser('~/catch/catch_database.db')}", echo=False)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

print(session)

print("Database connection established.")
