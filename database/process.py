from database.models.image.crud import ImageCRUD
from database.models.label.crud import LabelCRUD
from database.models.setting.crud import SettingCRUD


class DatabaseProcess:
    def __init__(self):
        self.image = ImageCRUD()
        self.label = LabelCRUD()
        self.setting = SettingCRUD()