from database.models.label.model import Label
from database.crud import CRUD


from database import session


class LabelCRUD(CRUD):
    def __init__(self):
        super().__init__()


    @staticmethod
    def add(unique_id: str, name: str, is_default: bool) -> Label:
        if session.query(Label).filter(Label.unquie_id == unique_id).first() is not None:
            return None
        else:
            new_item = Label(unquie_id=unique_id, name=name, is_default=is_default)
            session.add(new_item)
            session.commit()
            return new_item
    
    @staticmethod
    def get():
        return session.query(Label)

    @staticmethod
    def update():
        pass
        
    @staticmethod
    def delete(item: Label) -> None:
        session.delete(item)
        session.commit()

    @staticmethod
    def filter(*args) -> list[Label]:
        return session.query(Label).filter(args[0] == args[1]).all()