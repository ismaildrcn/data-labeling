from PyQt5.QtWidgets import QGraphicsRectItem, QListWidgetItem
from PyQt5.QtCore import Qt

from label.widget import LabelWidget



class Labels(object):
    def __init__(self, connector=None):
        self._connector = connector
        self.label_widget = LabelWidget()

    def add(self, source, coords, rect_obj):
        widget = LabelWidget().setup(self._connector)
        widget.label_list.addItems([item[index] for index, item in enumerate(self._connector.configurator.label_list)])
        widget.label_list.setCurrentIndex(-1)

        item = QListWidgetItem(self._connector.current_label_list)
        item.setSizeHint(widget.main.sizeHint())
        self._connector.current_label_list.setItemWidget(item, widget.main)
        label = Label(source, coords, rect_obj, widget)
        print(label)
        widget.delete_label.clicked.connect(lambda: self.delete(label))
        widget.view_label.clicked.connect(lambda: self.hide(label))


    def hide(self, label):
        if label.rect_obj:
            label.rect_obj.setVisible(not label.rect_obj.isVisible())

    def delete(self, label):
        if label.rect_obj:
            # Sahneyi al
            scene = self._connector.scene
            
            # Rect'i sahneden sil
            if label.rect_obj in scene.items():
                scene.removeItem(label.rect_obj)
                # Rect'i memory'den temizle
                label.rect_obj = None
            
            # Widget'ı listeden bul ve sil
            list_widget = self._connector.current_label_list
            for index in range(list_widget.count()):
                item = list_widget.item(index)
                if list_widget.itemWidget(item) == label.widget.main:
                    # Widget'ı item'dan ayır
                    list_widget.setItemWidget(item, None)
                    # Item'ı listeden sil
                    list_widget.takeItem(index)
                    # Widget'ı daha sonra sil
                    label.widget.main.deleteLater()
                    break

class Label(object):
    def __init__(self, source, coords, rect_obj, widget: LabelWidget):
        self.source: str = source
        self.coords: tuple = coords
        self.rect_obj: QGraphicsRectItem = rect_obj
        self.widget: LabelWidget = widget