from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()



class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False)

    annotations = relationship("Annotation", back_populates="image")


class Annotation(Base):
    __tablename__ = 'annotations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    image_id = Column(Integer, ForeignKey('images.id'), nullable=False)
    label_id = Column(Integer, ForeignKey('labels.id'), nullable=False)

    label = Column(Integer, nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)

    image = relationship("Image", back_populates="annotations")
    label = relationship("Label", back_populates="annotations")


class Label(Base):
    __tablename__ = 'labels'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    is_default = Column(Boolean, nullable=False, default=False)

    annotations = relationship("Annotation", back_populates="label")