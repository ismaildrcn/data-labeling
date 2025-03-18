import sys

from PyQt5.QtWidgets import QApplication
from mains.connector import Connector



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Connector()
    window.show()
    sys.exit(app.exec_())