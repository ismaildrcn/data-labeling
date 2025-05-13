import os
import tempfile
from database.utils import UtilsForSettings


class Settings:
    def __init__(self, database=None):
        self._database = database
        self.create_temp_dir()
        if not self._database.setting.filter(UtilsForSettings.APPROVED.value):
            self._database.setting.update(UtilsForSettings.APPROVED.value, False)

    @property
    def use_default_labels(self):
        return bool(int(self._database.setting.filter(UtilsForSettings.USE_DEFAULT_LABELS.value).value))
    
    @property
    def session(self):
        return bool(int(self._database.setting.filter(UtilsForSettings.SESSION.value).value))
    
    @property
    def tempdir(self):
        return self._tempdir
    
    def create_temp_dir(self):
        self._tempdir = tempfile.TemporaryDirectory(prefix="catch_", suffix="_temp").name
        if not os.path.exists(self.tempdir):
            os.mkdir(self.tempdir)
        self._database.setting.update(UtilsForSettings.TEMP_URL.value, self.tempdir)
