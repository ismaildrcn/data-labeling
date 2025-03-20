
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QListWidgetItem, QListWidget, QGraphicsScene, QGraphicsView
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtCore import Qt, pyqtSlot


from templates.ui.mainWindow import Ui_MainWindow as UI
from widgets.graphics_view import CustomGraphicsView

from mains.listener import Listener
from label.configurator import Configurator
from label.labels import Labels





class Connector(QMainWindow, UI):
    def __init__(self):
        super().__init__()
        self.image_path_list = []
        self.start_pos = None
        self.rect_item = None
        self._current_source = None
        self.setupUi(self)
        self.initialize()
        self.connection()
        self.pages.setCurrentIndex(0)
        self.modules()
        self.show()

    def modules(self):
        self.listener = Listener(self)
        self.configurator = Configurator(self)
        self.labels = Labels(self)

    def connection(self):
        self.image_list.itemClicked.connect(self.load_selected_image)


    def initialize(self):
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.listWidget_label_list.setSpacing(5)

        self.graphicsView = CustomGraphicsView(self.centralwidget)
        self.graphicsView.rect_created_signal.connect(self.created_rect)
        self.graphicsView.setObjectName("graphicsView")
        self.layout_labeling_area.addWidget(self.graphicsView)
        
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        self.image_list.setViewMode(QListWidget.IconMode)
        self.image_list.setIconSize(QPixmap(125, 70).size())  # İkonları büyüt
        self.image_list.setGridSize(QPixmap(130, 75).size())  # Hücreleri genişlet
        
    @pyqtSlot(tuple)
    def created_rect(self, detail):
        """
            Yeni bir dikdörtgen oluşturulduğunda çağrılır.

            Bu method, yeni bir dikdörtgen oluşturulduğunda çağrılır ve
            dikdörtgenin koordinatlarını ve QGraphicsRectItem nesnesini alır.
            Bu bilgileri Labels sınıfına iletir ve etiketleme işlemini başlatır.

            Args:
                detail (tuple): Dikdörtgenin koordinatları ve QGraphicsRectItem nesnesi.
        """
        self.labels.add(self.current_source, detail[0], detail[1])
        
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
        self.current_source = item.data(Qt.UserRole)  # Listedeki resim yolunu al
        self.image_pixmap = QPixmap(self.current_source)

        self.scene.clear()  # Önceki sahneyi temizle
        pixmap_item = self.scene.addPixmap(self.image_pixmap)  # Yeni görseli ekle

        self.scene.setSceneRect(0, 0, self.image_pixmap.width(), self.image_pixmap.height())

        self.graphicsView.fitInView(pixmap_item, Qt.KeepAspectRatio)

        self.graphicsView.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.graphicsView.setResizeAnchor(QGraphicsView.NoAnchor)
        self.graphicsView.setRenderHint(QPainter.Antialiasing)

    @property
    def current_source(self):
        return self._current_source

    @current_source.setter
    def current_source(self, source):
        self._current_source = source