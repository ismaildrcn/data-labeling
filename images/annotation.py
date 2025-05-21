from typing import Union, overload

from PyQt5.QtWidgets import QGraphicsRectItem, QListWidgetItem

class Annotation(object):
    @overload
    def __init__(self, source: str, coords: tuple, rect_obj: QGraphicsRectItem, item: QListWidgetItem, db_item = None): ...
    @overload
    def __init__(self, source: str, coords: tuple, rect_obj: QGraphicsRectItem, item: QListWidgetItem, label: int, db_item = None): ...
    def __init__(self, **kwargs):
        """
            Belirtilen parametrelerle annotation nesnesini güncelle
            Args:
                db_item (Annotation): Güncellenecek annotation nesnesi
                image_id (int, optional): Yeni resim kimliği
                label_id (int, optional): Yeni etiket kimliği
                annotation_id (int, optional): Yeni annotation kimliği
                coord (tuple, optional): Yeni koordinatlar (x,y, genişlik, yükseklik)
            Returns:
                Union[Annotation, None]: Güncellenmiş annotation veya db_item sağlanmamışsa None
        """
        source: str = kwargs.get('source')
        coords: tuple = kwargs.get('coords')
        rect_obj: QGraphicsRectItem = kwargs.get('rect_obj')
        item: QListWidgetItem = kwargs.get('item')
        label: Union[int, None] = kwargs.get('label', None)
        db_item = kwargs.get('db_item', None)

        self.source: str = source
        self.coords: tuple = coords
        self.rect_obj: QGraphicsRectItem = rect_obj
        self.item: QListWidgetItem = item
        self.label: Union[int, None] = label if isinstance(label, int) else None
        self.db_item: Union[object, None] = db_item
        self.rect_index = None