from PyQt5.QtWidgets import QDialog, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QColor

from templates.ui.popup import Ui_Dialog as PopupUI
from modals.popup.messages import PopupMessages
from modals.popup.utils import Answers


class Popup(QDialog, PopupUI):
    def __init__(self, connector=None):
        super().__init__()
        self.setupUi(self)
        self._connector = connector
        self.initialize()
        self._answer = None


    def initialize(self):
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        shadow = QGraphicsDropShadowEffect(self._connector)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0))
        shadow.setOffset(0, 0)
        self.widget_main.setGraphicsEffect(shadow)

        self.pushButton_cancel.clicked.connect(self.cancel)
        self.pushButton_ok.clicked.connect(self.ok)

    def show(self, p_code: PopupMessages):
        self.widget_bottom_area.setVisible(True)
        self.pushButton_ok.setVisible(True)
        self.pushButton_cancel.setVisible(True)

        self.popup_code.setText(p_code.code)
        self.popup_message.setText(p_code.message)
        self.popup_type.setText(p_code.type)
        self.popup_icon.setPixmap(QPixmap(p_code.icon))
        if isinstance(p_code, PopupMessages.Info):
            self.widget_bottom_area.setVisible(False)
            super().show()
            QTimer.singleShot(2000, self.close)
        elif isinstance(p_code, PopupMessages.Warning) or isinstance(p_code, PopupMessages.Error):
            self.pushButton_cancel.setVisible(False)
            self.exec_()
            return self._answer
        else:
            self.exec_()
            return self._answer

    def cancel(self):
        self._answer = Answers.CANCEL
        self.close()

    def ok(self):
        self._answer = Answers.OK
        self.close()