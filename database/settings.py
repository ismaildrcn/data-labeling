
from database.utils import Tables


class Settings:
    def __init__(self, database=None):
        self._database = database

    @property
    def use_default_labels(self):
        return bool(int(self._database.label.get()))