import os
import sys

from PyQt5.QtWidgets import QApplication
from mains.connector import Connector
# High DPI ayarları
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)  # 1: SYSTEM_AWARE, 2: PER_MONITOR_AWARE

if not os.path.exists(os.path.expanduser("~/catch")):
    os.makedirs(os.path.expanduser("~/catch"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Connector()
    sys.exit(app.exec_())