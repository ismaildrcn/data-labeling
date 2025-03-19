
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
                    case self._connector.label_image_labeling_title:
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

            
            case QEvent.MouseMove:
                match source:
                    case self._connector.label_image_labeling_title:
                        if self.offset is not None and event.buttons() == Qt.LeftButton:
                            self._connector.move(event.globalPos() - self.offset)
            case QEvent.MouseButtonRelease:
                self.offset = None
        
        
        return super().eventFilter(source, event)