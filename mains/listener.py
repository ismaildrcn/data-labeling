from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtCore import QEvent, Qt

from modals.popup.messages import PopupMessages
from modals.popup.utils import Answers



class Listener(QMainWindow):
    def __init__(self, connector=None):
        super().__init__()
        self._connector = connector

        for widget in self._connector.findChildren(QWidget):
            widget.installEventFilter(self)

    
    def eventFilter(self, source, event):
        match event.type():
            case QEvent.MouseButtonDblClick | QEvent.MouseButtonPress:
                match source:
                    case self._connector.label_drop_images | self._connector.icon_drop_images:
                        self._connector.import_images()
                    case self._connector.label_image_labeling_title | self._connector.widget_top:
                        self.offset = event.globalPos() - self._connector.frameGeometry().topLeft()
                    case self._connector.pushButton_close_window:
                        self._connector.close()
                    case self._connector.pushButton_hide_window:
                        self._connector.showMinimized()
                    case self._connector.pushButton_fullscreen_window:
                        self.pushButton_fullscreen_window_event_changed()
                    case self._connector.pushButton_add_label:
                        self._connector.configurator.add()
                    case self._connector.pushButton_export_labels:
                        self._connector.configurator.export_labels()
                    case self._connector.label_import_labels | self._connector.icon_insert_label:
                        self._connector.configurator.import_labels()
                    case self._connector.pushButton_continue_labeling:
                        self.continue_event_changed()
                    case self._connector.pushButton_next_image:
                        self.next_or_previous_image_eventh_changed(1)
                    case self._connector.pushButton_previous_image:
                        self.next_or_previous_image_eventh_changed(-1)
                    case self._connector.pushButton_exit_project:
                        self.pushButton_exit_project_event_changed()
            case QEvent.KeyPress:
                if source == self._connector.pushButton_add_label and event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    self._connector.configurator.add()
            case QEvent.MouseMove:
                match source:
                    case self._connector.label_image_labeling_title | self._connector.widget_top:
                        if self.offset is not None and event.buttons() == Qt.LeftButton:
                            self._connector.move(event.globalPos() - self.offset)
            case QEvent.MouseButtonRelease:
                self.offset = None
            case QEvent.DragEnter:
                if source in (self._connector.icon_drop_images, self._connector.label_drop_images):
                    """Sadece dosya sürüklenirse kabul et"""
                    if event.mimeData().hasUrls():
                        event.acceptProposedAction()
            case QEvent.Drop:
                if source in (self._connector.icon_drop_images, self._connector.label_drop_images):
                    urls = event.mimeData().urls()
                    self._connector.import_images(urls)
                
        
        
        return super().eventFilter(source, event)
    
    def continue_event_changed(self) -> None:
        if self._connector.configurator.label_type:
            self._connector.pages.setCurrentIndex(2)
            self._connector.modals.popup.show(PopupMessages.Info.M100)
            if self._connector.image_list.count() > 0:
                self._connector.load_selected_image(self._connector.image_list.item(0))
            self._connector.label_total_image_value.setText(str(self._connector.image_list.count()))
        else:
            self._connector.modals.popup.show(PopupMessages.Error.M300)

    def pushButton_fullscreen_window_event_changed(self) -> None:
        if self._connector.isFullScreen():
            self._connector.showNormal()
        else:
            self._connector.showFullScreen()

    def next_or_previous_image_eventh_changed(self, transaction):
        current_item = self._connector.image_list.currentItem()
        if current_item:
            # Mevcut itemın index'ini al
            current_index = self._connector.image_list.indexFromItem(current_item).row()
            total_items = self._connector.image_list.count()
            
            # Bir sonraki index'i hesapla
            next_index = current_index + transaction
            
            # Liste sınırları içinde mi kontrol et
            if  0 <= next_index < total_items:
                next_item = self._connector.image_list.item(next_index)
                self._connector.image_list.setCurrentItem(next_item)
                self._connector.load_selected_image(next_item)
    
    def pushButton_exit_project_event_changed(self):
        answer = self._connector.show_message(PopupMessages.Action.M402)
        if answer == Answers.OK:
            self._connector.clear_project()