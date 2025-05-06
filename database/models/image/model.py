from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


from database import Base



class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False)

    annotations = relationship("Annotation", back_populates="image")
