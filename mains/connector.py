
from PyQt5.QtWidgets import QMainWindow

from templates.ui.mainWindow import Ui_MainWindow as UI




class Connector(QMainWindow, UI):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()



    def import_images(self):
        pass