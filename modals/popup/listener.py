from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtCore import QEvent, Qt



class Listener(QMainWindow):
    def __init__(self, popup):
        super().__init__()
        self._popup = popup
        
        for widget in self._popup.findChildren(QWidget):
            widget.installEventFilter(self)
    
    def eventFilter(self, source, event):
        keys = (Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5, Qt.Key_6, Qt.Key_7, Qt.Key_8, Qt.Key_9, Qt.Key_0)
        
        match event.type():
            case QEvent.Type.KeyPress:
                if event.key() in keys:
                    self.enter_digit(source)
                elif event.key() == Qt.Key_Backspace:
                    self.clear_digit(source)
                elif event.key() in (Qt.Key_Return, Qt.Key_Enter) and source == self._popup.lineEdit_verify_6:
                    self._popup.pushButton_ok.click()
                elif event.key() == Qt.Key_Escape:
                    return True


        return super().eventFilter(source, event)
    
    def enter_digit(self, source):
        match source:
            case self._popup.lineEdit_verify_1:
                self._popup.lineEdit_verify_2.setFocus()
            case self._popup.lineEdit_verify_2:
                self._popup.lineEdit_verify_3.setFocus()
            case self._popup.lineEdit_verify_3:
                self._popup.lineEdit_verify_4.setFocus()
            case self._popup.lineEdit_verify_4:
                self._popup.lineEdit_verify_5.setFocus()
            case self._popup.lineEdit_verify_5:
                self._popup.lineEdit_verify_6.setFocus()

    def clear_digit(self, source):
        match source:
            case self._popup.lineEdit_verify_1:
                self._popup.lineEdit_verify_1.setFocus()
            case self._popup.lineEdit_verify_2:
                self._popup.lineEdit_verify_2.setFocus() if self.check_clear(self._popup.lineEdit_verify_2) else self._popup.lineEdit_verify_1.setFocus()
            case self._popup.lineEdit_verify_3:
                self._popup.lineEdit_verify_3.setFocus() if self.check_clear(self._popup.lineEdit_verify_3) else self._popup.lineEdit_verify_2.setFocus()
            case self._popup.lineEdit_verify_4:
                self._popup.lineEdit_verify_4.setFocus() if self.check_clear(self._popup.lineEdit_verify_4) else self._popup.lineEdit_verify_3.setFocus()
            case self._popup.lineEdit_verify_5:
                self._popup.lineEdit_verify_5.setFocus() if self.check_clear(self._popup.lineEdit_verify_5) else self._popup.lineEdit_verify_4.setFocus()
            case self._popup.lineEdit_verify_6:
                self._popup.lineEdit_verify_6.setFocus() if self.check_clear(self._popup.lineEdit_verify_6) else self._popup.lineEdit_verify_5.setFocus()
    
    def check_clear(self, source):
        if source.text() == '':
            return False
        else:
            return True