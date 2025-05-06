
class Settings:
    def __init__(self, database=None):
        self._database = database

    @property
    def use_default_labels(self):
        return bool(int(self._database.setting.filter("use_default_labels").value))
    
    @property
    def session(self):
        return bool(int(self._database.setting.filter("session").value))