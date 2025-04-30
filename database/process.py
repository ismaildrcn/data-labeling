from database.models.image.crud import ImageCRUD
from database.models.label.crud import LabelCRUD
from database.models.setting.crud import SettingCRUD
from database.models.annotation.crud import AnnotationCRUD

from database.settings import Settings


class DatabaseProcess:
    def __init__(self):
        self.image = ImageCRUD()
        self.label = LabelCRUD()
        self.setting = SettingCRUD()
        self.annotation = AnnotationCRUD()

        self.settings = Settings(self)