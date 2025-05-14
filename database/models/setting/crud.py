from database.models.setting.model import Setting
from database.crud import CRUD

from database import session


class SettingCRUD(CRUD):
    def __init__(self):
        super().__init__()
        self.update("use_default_labels", True)
        session = self.filter("session")
        if session is None:
            self.add("session", False)

    @staticmethod
    def add(name: str, value: str) -> int:
        new_setting = Setting(name=name, value=value)
        session.add(new_setting)
        session.commit()
        return new_setting
    
    @staticmethod
    def get():
        return session.query(Setting)
    
    @staticmethod
    def update(name: str, value) -> None:
        setting = session.query(Setting).filter(Setting.name == name).first()
        if setting:
            setting.value = value
        else:
            setting = Setting(name=name, value=value)
            session.add(setting)
        session.commit()

    @staticmethod
    def filter(name: str):
        return session.query(Setting).filter(Setting.name == name).first()