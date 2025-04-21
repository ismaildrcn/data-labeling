from database.models import Image
from database.models import Annotation

from database import session
from database.utils import Tables

class Database:
    def __init__(self):
        pass

    def add(self, *args) -> int:
        if args[0] == Tables.IMAGE:
            new_item = Image(url=args[1])
        elif args[0] == Tables.ANNOTATION:
            new_item = Annotation(image_id=args[1], label=args[2], x=args[3][0], y=args[3][1], width=args[3][2], height=args[3][3])
        session.add(new_item)
        session.commit()
        return new_item.id

    def get(self, *args):
        if args[0] == Tables.IMAGE:
            items = session.query(Image).all()
        elif args[0] == Tables.ANNOTATION:
            items = session.query(Annotation).filter(Annotation.image_id == args[1]).all()
        return items