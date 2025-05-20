from typing import Union
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot

from database.utils import UtilsForSettings
from modals.popup.messages import PopupMessages
from templates.ui.login import Ui_Dialog as LoginUI
from account.users import User, Users

class Login(QDialog, LoginUI):
    userSignal = pyqtSignal(object)
    def __init__(self, connector=None):
        super().__init__()
        self.answer = None
        self._connector = connector
        self.setupUi(self)
        self.initialize()

    def initialize(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.connection()
        self.widget_main.setGraphicsEffect(self._connector.create_shadow())

        remember_me = self._connector.database.setting.filter(UtilsForSettings.REMEMBER_ME.value)
        if remember_me.value:
            self.lineEdit_username.setText(remember_me.value)
            self.checkBox_remember_me.setChecked(True)
            self.lineEdit_password.setFocus()

    def connection(self):
        self.pushButton_login.clicked.connect(self.check_login_input)
        self.pushButton_operator_continue.clicked.connect(lambda: self.check_login_input(operator=True))
        self.userSignal.connect(self.accept_login)
    
    def show(self):
        self.exec()
        return self.answer

    def check_login_input(self, operator: bool = False) -> None:
        if operator:
            self.userSignal.emit(Users["operator"].value)
        else:
            username = self.lineEdit_username.text()
            password = self.lineEdit_password.text()
            try:
                user = Users[username].value
                self.userSignal.emit(user if user.password == password else False)
            except KeyError:
                return self.userSignal.emit(None)
    
    @pyqtSlot(object)
    def accept_login(self, value):
        self.answer = value
        if value:
            self._connector.label_account_username.setText(value.username)
            self.lineEdit_username.clear()
            self.lineEdit_password.clear()
            if value is not Users["operator"].value:
                if self.checkBox_remember_me.isChecked():
                    self._connector.database.setting.update(UtilsForSettings.REMEMBER_ME.value, value.username)
                else:
                    self._connector.database.setting.update(UtilsForSettings.REMEMBER_ME.value, None)
            self.close()
        elif value is False:
            self._connector.show_message(PopupMessages.Warning.M205)
        else:
            self._connector.show_message(PopupMessages.Warning.M204)
        self.user = value
    
    @property
    def user(self) -> Union[User, bool]:
        return self._user
    
    @user.setter
    def user(self, value: Union[User, bool]) -> None:
        self._user = value

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            event.ignore()
        else:
            super().keyPressEvent(event)