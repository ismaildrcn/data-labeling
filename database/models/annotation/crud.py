from typing import Union
from database.models.annotation.model import Annotation
from database.crud import CRUD

from database import session

class AnnotationCRUD(CRUD):
    def __init__(self):
        super().__init__()
    
    @staticmethod
    def add(image_id: int, label_id: int, annotation_id, coord: tuple) -> Annotation:
        db_item = Annotation(image_id=image_id, label_id=label_id, annotation_id=annotation_id, x=coord[0], y=coord[1], width=coord[2], height=coord[3])
        session.add(db_item)
        session.commit()
        return db_item
    
    @staticmethod
    def get():
        return session.query(Annotation)
    
    @staticmethod
    def delete(item: Annotation) -> None:
        session.delete(item)
        session.commit()
    
    @staticmethod
    def update(**kwargs) -> Union[Annotation, None]:
        db_item = kwargs.get("db_item")
        image_id = kwargs.get("image_id")
        label_id = kwargs.get("label_id")
        annotation_id = kwargs.get("annotation_id")
        coord = kwargs.get("coord")

        if db_item:
            if image_id is not None:
                db_item.image_id = image_id
            if label_id is not None:
                db_item.label_id = label_id
            if annotation_id is not None:
                db_item.annotation_id = annotation_id
            if coord is not None:
                db_item.x = coord[0]
                db_item.y = coord[1]
                db_item.width = coord[2]
                db_item.height = coord[3]

            session.commit()
            return db_item
        else: 
            return None
    
    @staticmethod
    def filter(**kwargs) -> list[Annotation]:
        image_id = kwargs.get("image_id")
        return session.query(Annotation).filter(Annotation.image_id == image_id).filter(Annotation.label_id == None).all()
 
    @staticmethod
    def current_count(image_id: int) -> int:
        return session.query(Annotation).filter(Annotation.image_id == image_id).count()
    
    @staticmethod
    def count() -> int:
        return session.query(Annotation).count()
    
    @staticmethod
    def defined_count() -> int:
        return session.query(Annotation).filter(Annotation.label_id != None).count()
    
    @staticmethod
    def clear() -> None:
        for item in session.query(Annotation).all():
            session.delete(item)
        session.commit()