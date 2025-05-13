from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QPixmap

from images.image import TableImageContent 
from images.utils import ImageStatus


class ImageCore(object):
    def __init__(self, connector=None, image: QUrl=None):
        self._connector = connector
        self._connector.image_handler.check_directroy(image)
        self._annotations = []
        self.image_content = TableImageContent(connector.image_table, image)
        self.image_content.delete_image.clicked.connect(lambda: self._connector.image_handler.delete_image(image))

    def set_status(self, status: ImageStatus):
        self.image_content.status_item.setPixmap(QPixmap(status.icon))
    
    def add_annotation(self, annotation):
        self._annotations.append(annotation)
    
    def remove_annotation(self, annotation):
        self._annotations.remove(annotation)
    
    @property
    def row_index(self):
        return self.image_content.row_index
    
    @row_index.setter
    def row_index(self, index):
        self.image_content.row_index = index