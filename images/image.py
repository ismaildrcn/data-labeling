import os

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidgetItem, QLabel, QPushButton
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QUrl



class TableImageContent(object):
    def __init__(self, table=None, url: QUrl = None):
        self.setup(table, url)

    def setup(self, table,  image: QUrl):
        self.row_index = table.rowCount()
        table.setRowCount(self.row_index + 1)
        
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

        # Delete item
        self.delete_image = QPushButton()
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(":/images/templates/images/delete.svg"), QIcon.Normal, QIcon.Off)
        self.delete_image.setIcon(icon1)
        # self.delete_image.setScaledContents(True)
        self.delete_image.setFixedSize(22, 22)
        # self.delete_image.setAlignment(Qt.AlignCenter)
        
        # Label'ı container içinde ortala
        self.delete_container = QWidget()
        self.delete_layout = QHBoxLayout(self.delete_container)
        self.delete_layout.setContentsMargins(0, 0, 0, 0)  # Kenar boşluklarını kaldır
        self.delete_layout.addWidget(self.delete_image, 0, Qt.AlignCenter)  # Label'ı merkeze hizala
    
        
        # Name item  
        name_item = QTableWidgetItem()
        name_item.setText(os.path.basename(image.toLocalFile()))
        name_item.setData(Qt.UserRole, image)
        
        
        table.setCellWidget(self.row_index, 0, self.container)
        table.setItem(self.row_index, 1, name_item)
        table.setCellWidget(self.row_index, 2, self.delete_container)