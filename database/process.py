from database.models.image.crud import ImageCRUD
from database.models.label.crud import LabelCRUD
from database.models.setting.crud import SettingCRUD
from database.models.annotation.crud import AnnotationCRUD

from database.settings import Settings
from database.utils import UtilsForSettings

class DatabaseProcess:
    def __init__(self):
        self.image = ImageCRUD()
        self.label = LabelCRUD()
        self.setting = SettingCRUD()
        self.annotation = AnnotationCRUD()

        self.settings = Settings(self)
    
    def clear(self):
        self.annotation.clear()
        self.image.clear()
        self.label.clear()
        self.setting.update(UtilsForSettings.USE_DEFAULT_LABELS.value, True)
        self.setting.update(UtilsForSettings.SESSION.value, False)
        self.settings.create_temp_dir()