from enum import Enum

from database.models.image.model import Image
from database.models.annotation.model import Annotation
from database.models.label.model import Label
from database.models.setting.model import Setting

class Tables(Enum):
    """Enum for database tables."""
    IMAGE = Image
    ANNOTATION = Annotation
    LABEL = Label
    SETTING = Setting

class UtilsForSettings(Enum):
    """Enum for database settings."""
    USE_DEFAULT_LABELS = "use_default_labels"
    SESSION = "session"
    TEMP_URL = "temp_url"