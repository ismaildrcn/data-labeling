from typing import Union

from PyQt5.QtWidgets import QGraphicsRectItem, QListWidgetItem

class Annotation(object):
    def __init__(self, source, coords, rect_obj, item, label = None):
        self.source: str = source
        self.coords: tuple = coords
        self.rect_obj: QGraphicsRectItem = rect_obj
        self.label: Union[int, None] = label
        self.item: QListWidgetItem = item