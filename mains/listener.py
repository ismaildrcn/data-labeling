
from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtCore import QEvent, Qt



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
                    case self._connector.label_drop_images:
                        self._connector.import_images()
                    case self._connector.label_image_labeling_title | self._connector.widget_top:
                        self.offset = event.globalPos() - self._connector.frameGeometry().topLeft()
                    case self._connector.pushButton_close_window:
                        self._connector.close()
                    case self._connector.pushButton_hide_window:
                        self._connector.showMinimized()
                    case self._connector.pushButton_fullscreen_window:
                        if self._connector.isFullScreen():
                            self._connector.showNormal()
                        else:
                            self._connector.showFullScreen()
                    case self._connector.pushButton_add_label:
                        self._connector.labels.add()
                    case self._connector.pushButton_export_labels:
                        self._connector.labels.export_labels()
                    case self._connector.label_import_labels:
                        self._connector.labels.import_labels()
                    case self._connector.pushButton_continue_labeling:
                        self._connector.pages.setCurrentIndex(2)
            case QEvent.KeyPress:
                if source == self._connector.pushButton_add_label and event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    self._connector.labels.add()
            case QEvent.MouseMove:
                match source:
                    case self._connector.label_image_labeling_title | self._connector.widget_top:
                        if self.offset is not None and event.buttons() == Qt.LeftButton:
                            self._connector.move(event.globalPos() - self.offset)
            case QEvent.MouseButtonRelease:
                self.offset = None
        
        
        return super().eventFilter(source, event)