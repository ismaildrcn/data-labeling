import os
import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtNetwork import QLocalServer, QLocalSocket
from mains.connector import Connector
# High DPI ayarları
import winreg
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)  # 1: SYSTEM_AWARE, 2: PER_MONITOR_AWARE

if not os.path.exists(os.path.expanduser("~/catch")):
    os.makedirs(os.path.expanduser("~/catch"))


APP_ID = 'catch_virtual_data_labeling'  # Benzersiz bir isim verin

def is_another_instance_running():
    try:
        socket = QLocalSocket()
        socket.connectToServer(APP_ID)
        if socket.waitForConnected(500):  # Bağlantı için biraz daha uzun süre bekleyelim
            socket.disconnectFromServer()
            socket.close()
            return True
    except Exception as e:
        print(f"Bağlantı kontrolü sırasında hata: {e}")
    return False

def create_local_server():
    server = QLocalServer()
    server.removeServer(APP_ID)  # Önceki hatalı kapanma durumlarını temizler
    if not server.listen(APP_ID):
        print(f"Server başlatılamadı: {server.errorString()}")
        return None
    return server

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Komut satırından dosya argümanı kontrolü
    anns_file = None
    if len(sys.argv) > 1 and sys.argv[1].endswith('.anns'):
        anns_file = sys.argv[1]

    if is_another_instance_running():
        print("Uygulama zaten çalışıyor. Lütfen mevcut pencereyi kullanın.")
        sys.exit()

    server = create_local_server()
    if not server:
        print("Local server oluşturulamadı. Uygulama kapatılıyor.")
        sys.exit()

    window = Connector(QUrl.fromLocalFile(anns_file) if anns_file else None)
    sys.exit(app.exec_())