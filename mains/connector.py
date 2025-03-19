
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QListWidgetItem, QListWidget, QGraphicsScene, QGraphicsView
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QRectF, QPointF


from templates.ui.mainWindow import Ui_MainWindow as UI
from mains.listener import Listener

from widgets.graphics_view import CustomGraphicsView




class Connector(QMainWindow, UI):
    def __init__(self):
        super().__init__()
        self.image_path_list = []
        self.start_pos = None
        self.rect_item = None
        self.setupUi(self)
        self.initialize()
        self.connection()
        self.pages.setCurrentIndex(0)
        self.modules()
        self.show()

    def modules(self):
        self.listener = Listener(self)

    def connection(self):
        self.image_list.itemClicked.connect(self.load_selected_image)


    def initialize(self):
        self.setWindowFlags(Qt.FramelessWindowHint)


        self.graphicsView = CustomGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName("graphicsView")
        self.layout_labeling_area.addWidget(self.graphicsView)
        
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        self.image_list.setViewMode(QListWidget.IconMode)
        # self.image_list.setSpacing(10)
        self.image_list.setIconSize(QPixmap(150, 85).size())  # İkonları büyüt
        self.image_list.setGridSize(QPixmap(155, 90).size())  # Hücreleri genişlet
        
    def import_images(self):
        self.image_path_list = QFileDialog.getOpenFileNames(self, "Import Images", "", "Images (*.png *.jpg *.jpeg)")[0]

        for image in self.image_path_list:
            self.create_image_list(image)
        if self.image_path_list:
            self.pages.setCurrentIndex(1)
        
    def create_image_list(self, image):
        item = QListWidgetItem(QIcon(image), None)  # QIcon ile resimleri ekle
        item.setData(Qt.UserRole, image)  # Görsel yolunu sakla
        self.image_list.addItem(item)

    
    def load_selected_image(self, item):
        """ Seçilen görseli yükle """
        image_path = item.data(Qt.UserRole)  # Listedeki resim yolunu al
        self.image_pixmap = QPixmap(image_path)

        self.scene.clear()  # Önceki sahneyi temizle
        pixmap_item = self.scene.addPixmap(self.image_pixmap)  # Yeni görseli ekle

        self.scene.setSceneRect(0, 0, self.image_pixmap.width(), self.image_pixmap.height())

        self.graphicsView.fitInView(pixmap_item, Qt.KeepAspectRatio)

        self.graphicsView.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.graphicsView.setResizeAnchor(QGraphicsView.NoAnchor)
        self.graphicsView.setRenderHint(QPainter.Antialiasing)
