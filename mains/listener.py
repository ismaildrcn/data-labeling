from PyQt5.QtWidgets import QMainWindow, QWidget, QGraphicsView, QAction, QMenu
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QIcon, QPixmap

from modals.popup.messages import PopupMessages
from modals.popup.utils import Answers

import os


class Listener(QMainWindow):
    def __init__(self, connector=None):
        super().__init__()
        self._connector = connector
        self.offset = None
        for widget in self._connector.findChildren(QWidget):
            widget.installEventFilter(self)
        self._connector.image_table.viewport().installEventFilter(self)
    
    def eventFilter(self, source, event):
        match event.type():
            case QEvent.MouseButtonPress:
                if event.spontaneous() and source.isEnabled():
                    if source.parent() == self._connector.image_table:
                        source = source.parent()
                    match source:
                        case self._connector.label_drop_images | self._connector.icon_drop_images | self._connector.widget_importing_area:
                            self._connector.image_handler.insert_image()
                        case self._connector.label_image_labeling_title | self._connector.widget_top:
                            self.offset = event.globalPos() - self._connector.frameGeometry().topLeft()
                        case self._connector.pushButton_close_window:
                            self._connector.close()
                        case self._connector.pushButton_hide_window:
                            self._connector.showMinimized()
                        case self._connector.pushButton_fullscreen_window:
                            self.pushButton_fullscreen_window_event_changed()
                        case self._connector.pushButton_add_label:
                            self._connector.configurator.add()
                        case self._connector.pushButton_export_labels:
                            self._connector.configurator.export_labels()
                        case self._connector.label_import_labels | self._connector.icon_insert_label:
                            self._connector.configurator.import_labels()
                        case self._connector.pushButton_continue_labeling:
                            self.continue_event_changed()
                        case self._connector.pushButton_next_image:
                            self.next_or_previous_image_eventh_changed(1)
                        case self._connector.pushButton_previous_image:
                            self.next_or_previous_image_eventh_changed(-1)
                        case self._connector.pushButton_exit_project:
                            self.pushButton_exit_project_event_changed()
                        case self._connector.pushButton_activate_hand:
                            self._connector.graphicsView.setDragMode(QGraphicsView.ScrollHandDrag)
                        case self._connector.pushButton_activate_crosshair:
                            self._connector.graphicsView.setDragMode(QGraphicsView.NoDrag)
                        case self._connector.pushButton_zoom_in:
                            self._connector.graphicsView.zoom(1)
                        case self._connector.pushButton_zoom_out:
                            self._connector.graphicsView.zoom(-1)
                        case self._connector.pushButton_zoom_fit:
                            self._connector.reset_zoom()
                        case self._connector.icon_drop_project | self._connector.label_drop_project | self._connector.widget_import_project:
                            self._connector.image_handler.insert_project()
                        case self._connector.image_table:
                            self.image_table_event_changed(event)
                        case self._connector.pushButton_continue_labeling_from_images:
                            self._connector.pages.setCurrentIndex(2)

                    
            case QEvent.KeyPress:
                if source in (self._connector.pushButton_add_label, self._connector.lineEdit_add_label) and event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    self._connector.configurator.add()
            case QEvent.MouseMove:
                match source:
                    case self._connector.label_image_labeling_title | self._connector.widget_top:
                        if self.offset is not None and event.buttons() == Qt.LeftButton and not self._connector.isFullScreen():
                            self._connector.move(event.globalPos() - self.offset)
            case QEvent.MouseButtonRelease:
                self.offset = None
            case QEvent.DragEnter:
                if source in (
                    self._connector.icon_drop_images, self._connector.label_drop_images, self._connector.icon_drop_project, 
                    self._connector.label_drop_project, self._connector.widget_importing_area, self._connector.widget_import_project,
                    self._connector.image_table, self._connector.image_table.viewport(), self._connector.widget_image_list
                    ) and event.mimeData().hasUrls():
                        event.acceptProposedAction()
            case QEvent.Drop:
                if source in (
                    self._connector.icon_drop_images, self._connector.label_drop_images, self._connector.widget_importing_area,
                    self._connector.image_table, self._connector.image_table.viewport(), self._connector.widget_image_list
                    ):
                    urls = event.mimeData().urls()
                    file_urls = self.has_file(urls)
                    if file_urls:
                        self._connector.image_handler.insert_image(file_urls, route=source not in (self._connector.image_table, self._connector.image_table.viewport(), self._connector.widget_image_list))
                elif source in (
                    self._connector.label_drop_project, self._connector.icon_drop_project, self._connector.widget_import_project
                    ):
                    urls = event.mimeData().urls()
                    file_urls = self.has_file(urls)
                    if file_urls:
                        self._connector.image_handler.insert_project(file_urls)
        

        return super().eventFilter(source, event)

    def continue_event_changed(self) -> None:
        if self._connector.configurator.label_type:
            self._connector.pages.setCurrentIndex(2)
            if self._connector.first_start:
                self._connector.modals.popup.show(PopupMessages.Info.M100)
                if self._connector.image_table.rowCount() > 0:
                    self._connector.load_selected_image(0, 1)
                    self._connector.image_handler.set_dashboard_values()
                self._connector.first_start = False
        else:
            self._connector.modals.popup.show(PopupMessages.Error.M300)

    def pushButton_fullscreen_window_event_changed(self) -> None:
        if self._connector.isFullScreen():
            self._connector.showNormal()
            self._connector.centralLayout.setContentsMargins(9, 9, 9, 9)
        else:
            self._connector.centralLayout.setContentsMargins(0, 0, 0, 0)
            self._connector.showFullScreen()
            self._connector.reset_zoom()

    def next_or_previous_image_eventh_changed(self, transaction):
        current_item = self._connector.image_table.item(self._connector.image_table.currentRow(), 1)
        if current_item:
            # Mevcut itemın index'ini al
            current_index = self._connector.image_table.indexFromItem(current_item).row()
            total_items = self._connector.image_table.rowCount()
            
            # Bir sonraki index'i hesapla
            next_index = current_index + transaction
            
            # Liste sınırları içinde mi kontrol et
            if  0 <= next_index < total_items:
                self._connector.load_selected_image(next_index)
    
    def pushButton_exit_project_event_changed(self):
        answer = self._connector.show_message(PopupMessages.Action.M402)
        if answer == Answers.OK:
            answer = self._connector.show_message(PopupMessages.Verify.M501)
            if answer == Answers.OK:
                self._connector.clear_project()

    def image_table_event_changed(self, event):
        if event.button() == Qt.RightButton:
            menu = QMenu(self._connector.image_table)
            menu.setStyleSheet("""
                QMenu {
                    background-color: #222831;
                    border: 1px solid #3D3D3D;
                    border-radius: 3px;
                    padding: 5px;
                }
                QMenu::item {
                    color: white;
                    padding: 5px 30px 5px 30px;
                    margin: 2px;
                }
                QMenu::item:selected {
                    background-color: #393E46;
                    border-radius: 2px;
                }
            """)
            self._connector.create_action(
                    menu,
                    ":/images/templates/images/import-image.svg",
                    "Görsel Ekle",
                    lambda: self._connector.image_handler.insert_image(route=False)
                )
            clicked_item = self._connector.image_table.itemAt(event.pos())
            if clicked_item:
                self._connector.create_action(
                    menu, 
                    ":/images/templates/images/delete.svg", 
                    "Görseli Sil",
                    lambda: self._connector.image_handler.delete_image(
                            self._connector.image_table.item(clicked_item.row(), 1).data(Qt.UserRole)
                            )
                )
            # Menüyü göster
            menu.exec_(event.globalPos())

    @staticmethod
    def has_file(urls: list) -> list:
        # Sadece dosya olanları al
        file_urls = []
        for url in urls:
            local_path = url.toLocalFile()
            if os.path.isfile(local_path):
                file_urls.append(url)
        return file_urls