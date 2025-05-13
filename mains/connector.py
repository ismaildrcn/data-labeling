import sys

from typing import overload
from PyQt5.QtCore import Qt, pyqtSlot, QSize, QRegularExpression, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QRegularExpressionValidator
from PyQt5.QtWidgets import QMainWindow, QAbstractItemView, QGraphicsScene, QGraphicsView, QAction, QMenu, QTableWidgetItem

from modals.popup.utils import Answers
from templates.theme.colors import Colors
from templates.ui.mainWindow import Ui_MainWindow as UI
from widgets.graphics_view import CustomGraphicsView

from mains.listener import Listener
from mains.source import Source
from label.configurator import Configurator
from modals.modals import Modals
from modals.popup.messages import PopupMessages
from images.handler import ImageHandler

from database.process import DatabaseProcess
from database.utils import Tables




class Connector(QMainWindow, UI):
    def __init__(self):
        super().__init__()
        self.start_pos = None
        self.rect_item = None
        self.setupUi(self)
        self.connection()
        self.pages.setCurrentIndex(0)
        self.modules()
        self.initialize()

    def modules(self):
        self.listener = Listener(self)
        self.source = Source()
        self.database = DatabaseProcess()
        self.configurator = Configurator(self)
        self.modals = Modals(self)
        self.image_handler = ImageHandler(self)

    def connection(self):
        self.image_table.cellClicked.connect(self.load_selected_image)
        self.pushButton_actions.clicked.connect(self.show_menu)
        self.pages.currentChanged.connect(self.pages_current_changed)


    def initialize(self):
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.listWidget_label_list.setSpacing(5)

        self.graphicsView = CustomGraphicsView(self.centralwidget)
        self.graphicsView.rect_created_signal.connect(self.created_rect)
        self.graphicsView.setObjectName("graphicsView")
        self.layout_labeling_area.addWidget(self.graphicsView)
        
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        self.image_table.setColumnWidth(0, 40)
        self.image_table.setColumnWidth(1, 200)
        self.image_table.setColumnWidth(2, 40)
        self.image_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.image_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

        self.image_table.setIconSize(QSize(16, 16))  # Icon boyutunu ayarla

        regex = QRegularExpression("^[a-z]*$")
        validator = QRegularExpressionValidator(regex)
        self.lineEdit_add_label.setValidator(validator)

        self.init_actions()

        self.pushButton_exit_project.setVisible(False)
        self.show()

        # Yarım bırakılmış oturum varsa tüm çalışmayı veritabanından içeri aktarır.
        if self.database.settings.session:
            answer = self.show_message(PopupMessages.Action.M404)
            if answer == Answers.OK:
                self.image_handler.insert_from_database()
            else:
                answer = self.show_message(PopupMessages.Verify.M500)
                if answer == Answers.OK:
                    self.clear_project()
                else:
                    self.close()
                    sys.exit()


        
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
        self.image_handler.add_annotation(source=self.source.current, coords=detail[0], rect_obj=detail[1])

    @overload
    def load_selected_image(self, item: QTableWidgetItem) -> None: ...
    @overload
    def load_selected_image(self, row: int, column: int) -> None: ...  
    def load_selected_image(self, *args) -> None:
        if len(args) == 1:
            item = args[0]
        else:
            item = self.image_table.item(args[0], 1)
        """ Seçilen görseli yükle"""
        self.source.current = item.data(Qt.UserRole)  # Listedeki resim yolunu al
        if self.source.current != self.source.previous:
            self.image_pixmap = QPixmap(self.source.current.toLocalFile())

            self.scene.clear()  # Önceki sahneyi temizle
            pixmap_item = self.scene.addPixmap(self.image_pixmap)  # Yeni görseli ekle

            self.scene.setSceneRect(0, 0, self.image_pixmap.width(), self.image_pixmap.height())
            self.scene.setSceneRect(0, 0, self.image_pixmap.width(), self.image_pixmap.height())

            self.graphicsView.fitInView(pixmap_item, Qt.KeepAspectRatio)

            self.graphicsView.setTransformationAnchor(QGraphicsView.NoAnchor)
            self.graphicsView.setResizeAnchor(QGraphicsView.NoAnchor)
            self.graphicsView.setRenderHint(QPainter.Antialiasing)
            self.image_handler.add_multi_annotation(self.source)
            self.label_current_image_name.setText(f"{self.image_table.currentRow() + 1} - {self.source.current.toLocalFile().split('/')[-1]}")

    def init_actions(self):
        self.menu = QMenu(self)
        self.menu.setStyleSheet(f"""
            QMenu {{
                border: 1px solid #5678d5;
                background-color: {Colors.PRIMARY};
                color: #EEEEEE;
                padding: 8px;
            }}
            QMenu::item {{
                padding: 8px 10px;
                background-color: transparent;
            }}
            QMenu::item:selected {{
                background-color: #5678d5;
            }}
        """)

        import_images = QAction(QIcon(":/images/templates/images/import-image.svg"), "Görüntüleri Uygulamaya Aktar", self)
        import_images.triggered.connect(lambda: self.pages.setCurrentIndex(0))
        self.menu.addAction(import_images)

        edit_label = QAction(QIcon(":/images/templates/images/label.svg"), "Etiketleri Düzenle", self)
        edit_label.triggered.connect(lambda: self.pages.setCurrentIndex(1))
        self.menu.addAction(edit_label)

        import_action = QAction(QIcon(":/images/templates/images/database-import.svg"), "Çalışmayı Uygulamaya Aktar", self)
        # exit_action.triggered.connect(self.close)
        self.menu.addAction(import_action)
        
        export_action = QAction(QIcon(":/images/templates/images/database-export.svg"), "Çalışmayı Bilgisayara Aktar", self)
        export_action.triggered.connect(self.image_handler.export)
        self.menu.addAction(export_action)
        
        
    def show_menu(self):
        self.menu.exec_(self.pushButton_actions.mapToGlobal(self.pushButton_actions.rect().bottomLeft()))
    
    def show_message(self, p_code: PopupMessages):
        return self.modals.popup.show(p_code)

    def clear_project(self):
        self.scene.clear()
        self.image_pixmap = None

        self.configurator.reset()
        self.image_handler.clear()
        self.database.clear()
        
        self.current_label_list.clear()
        self.image_table.clearContents()
        self.image_table.setRowCount(0)
        self.source.clear()
        self.pages.setCurrentIndex(0)

    def pages_current_changed(self, index):
        if index == 2:
            self.pushButton_exit_project.setVisible(True)
            self.label_total_image_value.setText(str(self.image_handler.count))
            return
        self.pushButton_exit_project.setVisible(False)

    def reset_zoom(self):
        self.graphicsView.reset()
        self.graphicsView.resetTransform()
        self.graphicsView.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)