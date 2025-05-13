import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

if not os.path.exists(os.path.expanduser("~/catch")):
    os.makedirs(os.path.expanduser("~/catch"))

engine = create_engine(f"sqlite:///{os.path.expanduser('~/catch/catch_database.db')}", echo=False)

from database.models.image.model import Image
from database.models.label.model import Label 
from database.models.annotation.model import Annotation
from database.models.setting.model import Setting

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

print("Database connection established.")
