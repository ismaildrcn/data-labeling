import random

from PyQt5.QtWidgets import QDialog, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QTimer, QRegExp
from PyQt5.QtGui import QPixmap, QColor, QRegExpValidator

from templates.ui.popup import Ui_Dialog as PopupUI
from modals.popup.messages import PopupMessages
from modals.popup.listener import Listener
from modals.popup.utils import Answers


class Popup(QDialog, PopupUI):
    def __init__(self, connector=None):
        super().__init__()
        self.setupUi(self)
        self._connector = connector
        self.listener = Listener(self)
        self.initialize()
        self._answer = None
        self._p_code = None


    def initialize(self):
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        shadow = QGraphicsDropShadowEffect(self._connector)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0))
        shadow.setOffset(0, 0)

        validator = QRegExpValidator(QRegExp("[0-9]"), self)

        self.lineEdit_verify_1.setValidator(validator)
        self.lineEdit_verify_2.setValidator(validator)
        self.lineEdit_verify_3.setValidator(validator)
        self.lineEdit_verify_4.setValidator(validator)
        self.lineEdit_verify_5.setValidator(validator)
        self.lineEdit_verify_6.setValidator(validator)

        self.widget_main.setGraphicsEffect(shadow)

        self.pushButton_cancel.clicked.connect(self.cancel)
        self.pushButton_ok.clicked.connect(self.ok)

    def show(self, p_code: PopupMessages):
        self._p_code = p_code
        if isinstance(p_code, PopupMessages.Verify):
            self.generate_verify_key()
            self.clear_verify_area()
            self.widget_verify_area.setVisible(True)
            self.lineEdit_verify_1.setFocus()
        else:
            self.widget_verify_area.setVisible(False)

        self.widget_bottom_area.setVisible(True)
        self.pushButton_ok.setVisible(True)
        self.pushButton_cancel.setVisible(True)

        self.popup_code.setText(p_code.code)
        self.popup_message.setText(p_code.message.replace('&param', f"{self.verify_key}") if isinstance(p_code, PopupMessages.Verify) else p_code.message)
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
        if isinstance(self._p_code, PopupMessages.Verify):
            if self.check_verify_code:
                self.close()
        else:
            self.close()

    def generate_verify_key(self):
        self.verify_key = random.randint(100000, 999999)
    
    def clear_verify_area(self):
        self.lineEdit_verify_1.clear()
        self.lineEdit_verify_2.clear()
        self.lineEdit_verify_3.clear()
        self.lineEdit_verify_4.clear()
        self.lineEdit_verify_5.clear()
        self.lineEdit_verify_6.clear()
    
    @property
    def check_verify_code(self):
        verify_1 = self.lineEdit_verify_1.text()
        verify_2 = self.lineEdit_verify_2.text()
        verify_3 = self.lineEdit_verify_3.text()
        verify_4 = self.lineEdit_verify_4.text()
        verify_5 = self.lineEdit_verify_5.text()
        verify_6 = self.lineEdit_verify_6.text()
        user_code = f"{verify_1}{verify_2}{verify_3}{verify_4}{verify_5}{verify_6}"
        if user_code.isnumeric() and self.verify_key == int(user_code):
            return True
        return False