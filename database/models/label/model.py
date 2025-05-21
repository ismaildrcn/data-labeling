from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship


from database import Base



class Label(Base):
    __tablename__ = 'labels'
    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_id = Column(Integer, unique=True)
    name = Column(String, nullable=False)
    is_default = Column(Boolean, nullable=False, default=False)

    annotations = relationship("Annotation", back_populates="label")
