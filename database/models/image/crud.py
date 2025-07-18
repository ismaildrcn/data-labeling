from database.models.image.model import Image
from database.crud import CRUD

from database import session


class ImageCRUD(CRUD):
    def __init__(self):
        super().__init__()

    @staticmethod
    def add(url: str, main_url) -> int:
        new_image = Image(url=url, main_url=main_url)
        session.add(new_image)
        session.commit()
        return new_image
    
    @staticmethod
    def get():
        return session.query(Image)

    @staticmethod
    def update(id: int, url: str) -> None:
        image = session.query(Image).filter(Image.id == id).first()
        if image:
            image.url = url
            session.commit()

    @staticmethod
    def delete(image: Image) -> None:
        session.delete(image)
        session.commit()

    @staticmethod
    def filter(url: str) -> Image:
        return session.query(Image).filter(Image.url == url).first()

    @staticmethod
    def count() -> int:
        return session.query(Image).count()
    
    @staticmethod
    def clear() -> None:
        for item in session.query(Image).all():
            session.delete(item)
        session.commit()