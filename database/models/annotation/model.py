from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship

from database import Base


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
