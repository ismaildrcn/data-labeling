
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QListWidgetItem, QListWidget, QGraphicsScene, QGraphicsView, QAction, QMenu, QDesktopWidget
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtCore import Qt, pyqtSlot, QUrl


from templates.ui.mainWindow import Ui_MainWindow as UI
from widgets.graphics_view import CustomGraphicsView

from mains.listener import Listener
from mains.source import Source
from label.configurator import Configurator
from annotation.annotation import Annotations
from modals.modals import Modals
from modals.popup.messages import PopupMessages





class Connector(QMainWindow, UI):
    def __init__(self):
        super().__init__()
        self.image_path_list = []
        self.start_pos = None
        self.rect_item = None
        self.setupUi(self)
        self.connection()
        self.pages.setCurrentIndex(0)
        self.modules()
        self.initialize()
        self.show()

    def modules(self):
        self.listener = Listener(self)
        self.source = Source()
        self.configurator = Configurator(self)
        self.annotations = Annotations(self)
        self.modals = Modals(self)

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

        self.init_actions()
        self.pushButton_actions.clicked.connect(self.show_menu)

        
    @pyqtSlot(tuple)
    def created_rect(self, detail):
        """
            Yeni bir dikdörtgen oluşturulduğunda çağrılır.

            Bu method, yeni bir dikdörtgen oluşturulduğunda çağrılır ve
            dikdörtgenin koordinatlarını ve QGraphicsRectItem nesnesini alır.
            Bu bilgileri Annotations sınıfına iletir ve etiketleme işlemini başlatır.

            Args:
                detail (tuple): Dikdörtgenin koordinatları ve QGraphicsRectItem nesnesi.
        """
        self.annotations.add(self.source.current, detail[0], detail[1])
        
    def import_images(self, drop_list=False):
        if drop_list:
            self.image_path_list = drop_list
        else:
            self.image_path_list = QFileDialog.getOpenFileNames(self, "Import Images", "", "Images (*.png *.jpg *.jpeg)")[0]
        print(self.image_path_list)
        for image in self.image_path_list:
            self.create_image_list(QUrl(image))
        if self.image_path_list:
            self.pages.setCurrentIndex(1)
        
    def create_image_list(self, image: QUrl):
        item = QListWidgetItem(QIcon(image.path()), None)  # QIcon ile resimleri ekle
        item.setData(Qt.UserRole, image)  # Görsel yolunu sakla
        self.image_list.addItem(item)

    
    def load_selected_image(self, item):
        """ Seçilen görseli yükle """
        self.source.current = item.data(Qt.UserRole)  # Listedeki resim yolunu al
        self.image_pixmap = QPixmap(self.source.current.path())

        self.scene.clear()  # Önceki sahneyi temizle
        pixmap_item = self.scene.addPixmap(self.image_pixmap)  # Yeni görseli ekle

        self.scene.setSceneRect(0, 0, self.image_pixmap.width(), self.image_pixmap.height())

        self.graphicsView.fitInView(pixmap_item, Qt.KeepAspectRatio)

        self.graphicsView.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.graphicsView.setResizeAnchor(QGraphicsView.NoAnchor)
        self.graphicsView.setRenderHint(QPainter.Antialiasing)
        self.annotations.multi_annotations(self.source)

    def init_actions(self):
        self.menu = QMenu(self)
        self.menu.setStyleSheet("""
            QMenu {
                border: 1px solid #1B262C;
                background-color: #0F4C75;
                color: #BBE1FA;
                padding: 8px;
            }
            QMenu::item {
                padding: 8px 10px;
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: #3282B8;
            }
        """)

        edit_label = QAction(QIcon(":/images/templates/images/label.svg"), "Edit Label", self)
        edit_label.triggered.connect(lambda: self.pages.setCurrentIndex(1))
        self.menu.addAction(edit_label)

        import_images = QAction(QIcon(":/images/templates/images/import-image.svg"), "Import Images", self)
        import_images.triggered.connect(lambda: self.pages.setCurrentIndex(0))
        self.menu.addAction(import_images)

        import_action = QAction(QIcon(":/images/templates/images/database-import.svg"), "Import Annotations", self)
        # exit_action.triggered.connect(self.close)
        self.menu.addAction(import_action)
        
        export_action = QAction(QIcon(":/images/templates/images/database-export.svg"), "Export Annotations", self)
        export_action.triggered.connect(self.annotations.export_annotations)
        self.menu.addAction(export_action)
        
        
    def show_menu(self):
        self.menu.exec_(self.pushButton_actions.mapToGlobal(self.pushButton_actions.rect().bottomLeft()))