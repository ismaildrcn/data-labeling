import os

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidgetItem, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QUrl



class TableImageContent(object):
    def __init__(self, table=None, url: QUrl = None):
        self.setup(table, url)

    def setup(self, table,  image: QUrl):
        current_row = table.rowCount()
        table.setRowCount(current_row + 1)
        
        # Status item
        self.status_item = QLabel()
        self.status_item.setPixmap(QPixmap(":/images/templates/images/close.svg"))
        self.status_item.setScaledContents(True)
        self.status_item.setFixedSize(22, 22)
        self.status_item.setAlignment(Qt.AlignCenter)
        
        # Label'ı container içinde ortala
        self.container = QWidget()
        self.layout = QHBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Kenar boşluklarını kaldır
        self.layout.addWidget(self.status_item, 0, Qt.AlignCenter)  # Label'ı merkeze hizala
    
        
        # Name item  
        name_item = QTableWidgetItem()
        name_item.setText(os.path.basename(image.toLocalFile()))
        name_item.setData(Qt.UserRole, image)
        
        
        table.setCellWidget(current_row, 0, self.container)
        table.setItem(current_row, 1, name_item)