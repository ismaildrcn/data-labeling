import sys

from typing import Union, overload
from PyQt5.QtCore import Qt, pyqtSlot, QSize, QRegularExpression, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QRegularExpressionValidator, QMovie
from PyQt5.QtWidgets import QMainWindow, QAbstractItemView, QGraphicsScene, QGraphicsView, QAction, QMenu, QLabel
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QApplication

from database.utils import UtilsForSettings
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

from account.login import Login
from account.users import Users



class Connector(QMainWindow, UI):
    def __init__(self):
        super().__init__()
        self.start_pos = None
        self.rect_item = None
        self.setupUi(self)
        self.connection()
        self.modules()
        self.initialize()

    def modules(self):
        self.listener = Listener(self)
        self.source = Source()
        self.database = DatabaseProcess()
        self.configurator = Configurator(self)
        self.modals = Modals(self)
        self.image_handler = ImageHandler(self)
        self.login = Login(self)

    def connection(self):
        self.image_table.cellClicked.connect(self.load_selected_image)
        self.pushButton_actions.clicked.connect(self.show_menu)
        self.pages.currentChanged.connect(self.pages_current_changed)


    def initialize(self):
        answer = self.login.show()
        if not answer:
            sys.exit()
        elif answer == Users.operator.value:
            self.widget_personel_state.setVisible(False)
        else:
            self.authorize_project(self.database.setting.filter(UtilsForSettings.AUTHORIZED.value).value, False)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Alternatif Qt çözümü
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        self.widget_main.setGraphicsEffect(self.create_shadow())


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
        self.image_table.setAcceptDrops(True)
        self.image_table.viewport().setAcceptDrops(True)
        self.image_table.setDragDropMode(QAbstractItemView.DropOnly)
        self.image_table.setIconSize(QSize(16, 16))  # Icon boyutunu ayarla

        regex = QRegularExpression("^[a-z_]*$")
        validator = QRegularExpressionValidator(regex)
        self.lineEdit_add_label.setValidator(validator)

        self.init_actions()
        self.pages.setCurrentIndex(0)

        self.pushButton_continue_labeling_from_images.setVisible(False)
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
        self.authorize_project()

    @overload
    def load_selected_image(self, row: int, column: int) -> None: ...  
    def load_selected_image(self, *args) -> None:
        if args[0] == -1:
            self.show_message(PopupMessages.Info.M103)
            self.clear_project()
            return

        item = self.image_table.item(args[0], 1)
        """ Seçilen görseli yükle"""
        self.source.current = item.data(Qt.UserRole)  # Listedeki resim yolunu al
        self.image_table.setCurrentItem(item)  # Seçili satırı güncelle
        if self.source.current != self.source.previous:
            self.image_pixmap = QPixmap(self.source.current.toLocalFile())

            self.scene.clear()  # Önceki sahneyi temizle
            pixmap_item = self.scene.addPixmap(self.image_pixmap)  # Yeni görseli ekle

            self.scene.setSceneRect(0, 0, self.image_pixmap.width(), self.image_pixmap.height())

            self.graphicsView.fitInView(pixmap_item, Qt.KeepAspectRatio)

            self.graphicsView.setTransformationAnchor(QGraphicsView.NoAnchor)
            self.graphicsView.setResizeAnchor(QGraphicsView.NoAnchor)
            self.graphicsView.setRenderHint(QPainter.Antialiasing)
            self.current_label_list.clear()
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
        import_action.triggered.connect(self.image_handler.insert_project)
        self.menu.addAction(import_action)
        
        export_action = QAction(QIcon(":/images/templates/images/database-export.svg"), "Çalışmayı Bilgisayara Aktar", self)
        export_action.triggered.connect(self.image_handler.export)
        self.menu.addAction(export_action)

        if self.login.user != Users.operator.value:
            authorize_action = QAction(QIcon(":/images/templates/images/authorize.svg"), "Çalışmayı Onayla", self)
            authorize_action.triggered.connect(lambda: self.authorize_project(self.login.user.username))
            self.menu.addAction(authorize_action)
        
        
    def show_menu(self):
        if len(self.menu.actions()) == 5: 
            self.menu.actions()[4].setVisible(self.pages.currentIndex() == 2)
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
        if index == 0:
            self.widget_import_project.setVisible(self.image_handler.count <= 0)
            self.pushButton_continue_labeling_from_images.setVisible(self.image_handler.count > 0)
        if index == 2:
            self.pushButton_exit_project.setVisible(True)
            self.label_total_image_value.setText(str(self.image_handler.count))
            return
        self.pushButton_exit_project.setVisible(False)

    def reset_zoom(self):
        self.graphicsView.reset()
        self.graphicsView.resetTransform()
        self.graphicsView.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def authorize_project(self, authorized: Union[str, None] = None, animation: bool = True):
        """
            Onaylama işlemini gerçekleştirir.
            Eğer onaylama işlemi başarılı olursa, animasyon gösterilir.
        """
        self.database.setting.update(UtilsForSettings.AUTHORIZED.value, authorized)
        self.pushButton_personel_state.setChecked(bool(authorized))
        self.label_authorized.setText(authorized if authorized else "Onaylanmamış")
        if authorized and animation:
            self.create_authorize_animation()

    def create_authorize_animation(self):
        """
            Shows an approval animation in the center of the application for 1.6 seconds
        """
        # Create a label for the animation
        animation_label = QLabel(self)
        animation_label.setFixedSize(100, 100)
        
        # Load and set the GIF animation
        movie = QMovie(":/images/templates/images/authorize.gif")  # Adjust path to your GIF
        movie.setScaledSize(animation_label.size())
        animation_label.setMovie(movie)
        
        # Center the label in the main window
        animation_label.setAlignment(Qt.AlignCenter)
        geometry = self.geometry()
        x = (geometry.width() - animation_label.width()) // 2
        y = (geometry.height() - animation_label.height()) // 2
        animation_label.move(x, y)
        
        # Set window flags to show on top
        animation_label.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # Start animation and show label
        movie.start()
        animation_label.show()
        
        # Create timer to hide and cleanup
        timer = QTimer(self)
        timer.singleShot(1600, lambda: self.cleanup_animation(animation_label, movie))

    def cleanup_animation(self, label, movie):
        """Helper method to cleanup the animation"""
        movie.stop()
        label.hide()
        label.deleteLater()
        
    def create_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(Qt.black)
        shadow.setOffset(0, 0)
        return shadow