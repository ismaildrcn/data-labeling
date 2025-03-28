import os
import tempfile

from typing import Union
from zipfile import ZipFile
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QListWidgetItem, QListWidget, QGraphicsScene, QGraphicsView, QAction, QMenu, QGraphicsRectItem
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtCore import Qt, pyqtSlot, QUrl


from templates.ui.mainWindow import Ui_MainWindow as UI
from widgets.graphics_view import CustomGraphicsView

from mains.listener import Listener
from mains.source import Source
from label.configurator import Configurator
from annotation.annotation import Annotations
from annotation.annotation import Annotation
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
        self.pushButton_actions.clicked.connect(self.show_menu)


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
        old_working = False
        if drop_list:
            for image in drop_list:
                if image.path().endswith((".png", ".jpg", ".jpeg")) and image not in self.image_path_list:
                    self.create_image_list(image)
                elif image.path().endswith(".zip"):
                    old_working = image
        else:
            selected_list = QFileDialog.getOpenFileNames(self, "Görselleri Uygulamaya Aktar", "", "Images (*.png *.jpg *.jpeg, *.zip)")[0]
            for image in selected_list:
                if image.endswith(".zip"):
                    old_working = QUrl.fromLocalFile(image)
                elif QUrl.fromLocalFile(image) not in self.image_path_list:
                        self.create_image_list(QUrl.fromLocalFile(image))
        
        self.import_old_working(old_working)
        if self.image_path_list:
            self.pages.setCurrentIndex(1)
        old_working = False
        
    def create_image_list(self, image: QUrl):
        item = QListWidgetItem(QIcon(image.toLocalFile()), None)  # QIcon ile resimleri ekle
        item.setData(Qt.UserRole, image)  # Görsel yolunu sakla
        self.image_list.addItem(item)
        self.image_path_list.append(image)
    
    def import_old_working(self, path: Union[QUrl, bool]):
        if path:
            with tempfile.TemporaryDirectory() as tmpdir:
                with ZipFile(path.toLocalFile(), 'r') as archive:
                    archive.extractall(tmpdir)  # Zip dosyasını çıkar
                    name_list = archive.namelist()
                    lbl = list(filter(lambda x: x.endswith('.lbl'), name_list))[0]
                    self.configurator.import_labels(tmpdir + '/' + lbl)
                    name_list.remove(lbl)
                    for file in name_list:
                        file = tmpdir + '/' + file
                        image = self.check_image_path_list(file)
                        if image:
                            with open(file, 'r') as ann_file:
                                for line in ann_file.readlines():
                                    line = line.strip().split()
                                    if len(line) == 5:
                                        coords = (float(line[1]), float(line[2]), float(line[3]), float(line[4]))
                                        rect_obj = QGraphicsRectItem()
                                        self.annotations.add(image, coords, rect_obj, int(line[0]))

                    for item in archive.namelist():
                        os.remove(tmpdir + '/' + item)
        
    def check_image_path_list(self, path: str) -> Union[QUrl, bool]:
        for image in self.image_path_list:
            if '.'.join(image.toLocalFile().split("/")[-1].split('.')[:-1]) == path.split("/")[-1].split(".")[0]:
                return image
        if path.endswith('.lbl'):
            return True
        return False
                
        
    def load_selected_image(self, item):
        """ Seçilen görseli yükle """
        self.source.current = item.data(Qt.UserRole)  # Listedeki resim yolunu al
        if self.source.current != self.source.previous:
            self.image_pixmap = QPixmap(self.source.current.toLocalFile())

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
                border: 1px solid #00969d;
                background-color: #00ADB5;
                color: #EEEEEE;
                padding: 8px;
            }
            QMenu::item {
                padding: 8px 10px;
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: #00969d;
            }
        """)

        edit_label = QAction(QIcon(":/images/templates/images/label.svg"), "Etiketleri Düzenle", self)
        edit_label.triggered.connect(lambda: self.pages.setCurrentIndex(1))
        self.menu.addAction(edit_label)

        import_images = QAction(QIcon(":/images/templates/images/import-image.svg"), "Görüntüleri Uygulamaya Aktar", self)
        import_images.triggered.connect(lambda: self.pages.setCurrentIndex(0))
        self.menu.addAction(import_images)

        import_action = QAction(QIcon(":/images/templates/images/database-import.svg"), "Çalışmayı Uygulamaya Aktar", self)
        # exit_action.triggered.connect(self.close)
        self.menu.addAction(import_action)
        
        export_action = QAction(QIcon(":/images/templates/images/database-export.svg"), "Çalışmayı Bilgisayara Aktar", self)
        export_action.triggered.connect(self.annotations.export_annotations)
        self.menu.addAction(export_action)
        
        
    def show_menu(self):
        self.menu.exec_(self.pushButton_actions.mapToGlobal(self.pushButton_actions.rect().bottomLeft()))
    
    def show_message(self, p_code: PopupMessages):
        return self.modals.popup.show(p_code)