from database.models.label.model import Label
from database.crud import CRUD


from database import session


class LabelCRUD(CRUD):
    def __init__(self):
        super().__init__()


    @staticmethod
    def add(name: str, is_default: bool) -> Label:
        if is_default:
            existing_label = session.query(Label).filter(Label.name == name).first()
            if existing_label:
                return existing_label
        # En yüksek unique_id değerini bul
        max_id = session.query(Label).order_by(Label.unique_id.desc()).first()
        new_unique_id = max_id.unique_id + 1 if max_id else 0
        
        # Yeni kayıt oluştur
        new_item = Label(unique_id=new_unique_id, name=name, is_default=is_default)
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
    
    @staticmethod
    def clear():
        for item in session.query(Label).filter(Label.is_default == False).all():
            session.delete(item)
        session.commit()