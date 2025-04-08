from enum import Enum



class ImageStatus(Enum):
    """
    Enum for image status.
    """
    UNANNOTATED = (0, ":/images/templates/images/close.svg")
    ANNOTATED = (1, ":/images/templates/images/tick-double.svg")

    @property
    def icon(self):
        return self.value[1]