import sys

from typing import Union, overload
from PyQt5.QtCore import Qt, pyqtSlot, QSize, QRegularExpression, QTimer, QUrl
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QRegularExpressionValidator, QMovie
from PyQt5.QtWidgets import QMainWindow, QAbstractItemView, QGraphicsScene, QGraphicsView, QAction, QMenu, QLabel
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QApplication, QButtonGroup

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
    def __init__(self, anns_file: Union[QUrl, None] = None):
        super().__init__()
        self.start_pos = None
        self.rect_item = None
        self.first_start = True
        self.anns_file = anns_file

        self.menu_style = f"""
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
        """

        self.setupUi(self)
        self.modules()
        self.init_widgets()
        self.connection()
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
        self.pushButton_actions.clicked.connect(lambda: self.show_menu(self.pushButton_actions, self.actions_menu))
        self.pushButton_user.clicked.connect(lambda: self.show_menu(self.pushButton_user, self.user_menu))
        self.pages.currentChanged.connect(self.pages_current_changed)
    
    def init_widgets(self):
        """
            Uygulama arayüzünü başlatır ve gerekli bileşenleri ayarlar. 
        """
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

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

        regex = QRegularExpression("^[a-zA-Z_]*$")
        validator = QRegularExpressionValidator(regex)
        self.lineEdit_add_label.setValidator(validator)

        self.pushButton_continue_labeling_from_images.setVisible(False)
        self.pushButton_exit_project.setVisible(False)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.addButton(self.pushButton_activate_hand)
        self.button_group.addButton(self.pushButton_activate_crosshair)

    def initialize(self):
        self.first_start = True
        self.login.show()

        self.init_actions()
        self.clear_widgets()
        self.show()
        # Yarım bırakılmış oturum varsa tüm çalışmayı veritabanından içeri aktarır.
        if self.database.settings.session:
            answer = self.show_message(PopupMessages.Action.M404)
            if answer == Answers.OK:
                self.image_handler.insert_from_database()
                self.first_start = False
            else:
                answer = self.show_message(PopupMessages.Verify.M500)
                if answer == Answers.OK:
                    self.clear_project()
                    self.start_app_with_anns_file(self.anns_file)
                else:
                    self.close()
                    sys.exit()
        else:
            self.start_app_with_anns_file(self.anns_file)


    def start_app_with_anns_file(self, anns_file: QUrl):
        """
            Uygulamayı bir .anns dosyası ile başlatır.
            Bu method, uygulama başlatıldığında eğer bir .anns dosyası verilmişse
            bu dosyayı içe aktarır ve etiketleme alanını hazırlar.
        """
        if anns_file:
            self.image_handler.insert_project([anns_file])
            self.first_start = False
        
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
        self.widget_labeling_area.setEnabled(True)
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
        self.actions_menu = QMenu(self)
        self.actions_menu.setStyleSheet(self.menu_style)

        self.user_menu = QMenu(self)
        self.user_menu.setStyleSheet(self.menu_style)

        self.create_action(self.actions_menu, ":/images/templates/images/import-image.svg", "Görüntüleri Uygulamaya Aktar", lambda: self.pages.setCurrentIndex(0))
        self.create_action(self.actions_menu, ":/images/templates/images/label.svg", "Etiketleri Düzenle", self.edit_action)
        self.create_action(self.actions_menu, ":/images/templates/images/database-import.svg", "Çalışmayı Uygulamaya Aktar", self.image_handler.insert_project)
        self.create_action(self.actions_menu, ":/images/templates/images/database-export.svg", "Çalışmayı Bilgisayara Aktar", self.image_handler.export)

        if self.login.user != Users.operator.value:
            self.create_action(self.actions_menu, ":/images/templates/images/authorize.svg", "Çalışmayı Onayla", lambda: self.authorize_project(self.login.user.username, warning=True))

        self.create_action(self.user_menu, ":/images/templates/images/logout.svg", "Oturumu Kapat", self.login.logout)

    def create_action(self, menu: QMenu, icon: str, text: str, slot: callable) -> QAction:
        """
            Yeni bir QAction oluşturur ve verilen ikon, metin ve slot ile ilişkilendirir.
            Bu method, menüdeki eylemleri oluşturmak için kullanılır.
            
            Args:
                icon (str): Eylem için ikonun yolu.
                text (str): Eylemin metni.
                slot (callable): Eylem tetiklendiğinde çağrılacak fonksiyon.

            Returns:
                QAction: Oluşturulan QAction nesnesi.
        """
        action = QAction(QIcon(icon), text, self)
        action.triggered.connect(slot)
        menu.addAction(action)
        return action
        
    def edit_action(self):
        """
            Etiketleri düzenlemek için menüdeki "Etiketleri Düzenle" seçeneğini tetikler.
            Bu, kullanıcıyı etiket düzenleme sayfasına yönlendirir.
        """
        if self.image_handler.count <= 0:
            self.show_message(PopupMessages.Warning.M207)
            return
        self.pages.setCurrentIndex(1)
    
    def show_menu(self, button, menu: QMenu = None):
        if menu is None:
            menu = self.actions_menu
        if len(menu.actions()) == 5:
            menu.actions()[4].setVisible(self.pages.currentIndex() == 2)
        menu.exec_(button.mapToGlobal(button.rect().bottomLeft()))

    def show_message(self, p_code: PopupMessages):
        return self.modals.popup.show(p_code)

    def clear_widgets(self):
        self.image_pixmap = None
        self.current_label_list.clear()
        self.image_table.clearContents()
        self.image_table.setRowCount(0)
        self.widget_labeling_area.setEnabled(False)
        self.label_image_directory.clear()
        self.pages.setCurrentIndex(0)
        self.source.clear()
        self.image_handler.image_dir_list.clear()

    def clear_project(self):
        self.scene.clear()

        self.configurator.reset()
        self.image_handler.clear()
        self.database.clear()
        self.clear_widgets()

    def pages_current_changed(self, index):
        self.widget_import_project.setVisible(self.image_handler.count <= 0 if not self.first_start else True)
        self.pushButton_continue_labeling_from_images.setVisible(self.image_handler.count > 0 if not self.first_start else False)
        if index == 2:
            self.pushButton_exit_project.setVisible(True)
            self.label_total_image_value.setText(str(self.image_handler.count))
            return
        self.pushButton_exit_project.setVisible(False)

    def reset_zoom(self):
        self.graphicsView.reset()
        self.graphicsView.resetTransform()
        self.graphicsView.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def authorize_project(self, authorized: Union[str, None] = None, animation: bool = True, warning: bool = False):
        """
            Onaylama işlemini gerçekleştirir.
            Eğer onaylama işlemi başarılı olursa, animasyon gösterilir.
        """
        if not warning or self.database.annotation.count() > 0:
            if warning and self.database.annotation.undefined_count() > 0:
                self.show_message(PopupMessages.Warning.M205)
                return
            self.database.setting.update(UtilsForSettings.AUTHORIZED.value, authorized)
            self.pushButton_personel_state.setChecked(bool(authorized))
            self.label_authorized.setText(authorized if authorized else "Onaylanmamış")
            if authorized and animation:
                self.create_authorize_animation()
        else:
            self.show_message(PopupMessages.Warning.M200)
    
    def is_project_authorized(self) -> bool:
        return bool(self.database.setting.filter(UtilsForSettings.AUTHORIZED.value).value)

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