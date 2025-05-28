import sys

from typing import Union
from PyQt5.QtWidgets import QDialog, QWidget, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QPoint

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
        self._drag_active = False
        self._drag_position = QPoint()
        self.setupUi(self)
        self.initialize()
        self.install_drag_events()

    def initialize(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.connection()
        self.widget_main.setGraphicsEffect(self._connector.create_shadow())

    def connection(self):
        self.pushButton_login.clicked.connect(self.check_login_input)
        self.pushButton_operator_continue.clicked.connect(lambda: self.check_login_input(operator=True))
        self.pushButton_show_password.clicked.connect(self.toggle_password_visibility)
        self.userSignal.connect(self.accept_login)
    
    def show(self):
        self.label_username_warning.setVisible(False)
        self.label_password_warning.setVisible(False)
        remember_me = self._connector.database.setting.filter(UtilsForSettings.REMEMBER_ME.value)
        if remember_me and remember_me.value:
            self.lineEdit_username.setText(remember_me.value)
            self.checkBox_remember_me.setChecked(True)
            self.lineEdit_password.setFocus()
        self.exec()
        if not self.answer:
            sys.exit()
        elif self.answer == Users.operator.value:
            self._connector.widget_personel_state.setVisible(False)
        else:
            self._connector.widget_personel_state.setVisible(True)
            self._connector.authorize_project(self._connector.database.setting.filter(UtilsForSettings.AUTHORIZED.value).value, False)
        return self.answer
    
    def logout(self):
        self._connector.close()
        self._connector.initialize()

    def check_login_input(self, operator: bool = False) -> None:
        if operator:
            self.userSignal.emit(Users["operator"].value)
        else:
            username = self.lineEdit_username.text()
            password = self.lineEdit_password.text()
            if "" in (username, password):
                if username == "":
                    self.label_username_warning.setVisible(True)
                else:
                    self.label_username_warning.setVisible(False)
                if password == "":
                    self.label_password_warning.setVisible(True)
                else:
                    self.label_password_warning.setVisible(False)
                return
            else:
                self.label_username_warning.setVisible(False)
                self.label_password_warning.setVisible(False)
            try:
                user = Users[username].value
                self.userSignal.emit(user if user.password == password else None)
            except KeyError:
                return self.userSignal.emit(None)
    
    @pyqtSlot(object)
    def accept_login(self, value):
        self.answer = value
        if value:
            self._connector.pushButton_user.setText(value.username)
            self.lineEdit_username.clear()
            self.lineEdit_password.clear()
            if value is not Users["operator"].value:
                if self.checkBox_remember_me.isChecked():
                    self._connector.database.setting.update(UtilsForSettings.REMEMBER_ME.value, value.username)
                else:
                    self._connector.database.setting.update(UtilsForSettings.REMEMBER_ME.value, None)
            self.close()
        else:
            self._connector.show_message(PopupMessages.Warning.M204)
        self.user = value
    
    @property
    def user(self) -> Union[User, bool]:
        return self._user
    
    @user.setter
    def user(self, value: Union[User, bool]) -> None:
        self._user = value

    def install_drag_events(self):
        def recursive_install(widget):
            # QLineEdit ve QPushButton hariç
            if widget.inherits("QLineEdit") or widget.inherits("QPushButton") or widget.inherits("QCheckBox"):
                return
            widget.installEventFilter(self)
            for child in widget.findChildren(QWidget):
                recursive_install(child)
        recursive_install(self)

    def eventFilter(self, obj, event):
        if event.type() == event.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                self._drag_active = True
                self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
                return True
        elif event.type() == event.MouseMove:
            if self._drag_active and event.buttons() & Qt.LeftButton:
                self.move(event.globalPos() - self._drag_position)
                return True
        elif event.type() == event.MouseButtonRelease:
            if self._drag_active:
                self._drag_active = False
                return True
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            event.ignore()
        else:
            super().keyPressEvent(event)
    
    def toggle_password_visibility(self):
        if self.pushButton_show_password.isChecked():
            self.lineEdit_password.setEchoMode(self.lineEdit_password.Normal)
        else:
            self.lineEdit_password.setEchoMode(self.lineEdit_password.Password)