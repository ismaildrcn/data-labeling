import os
import uuid
import json
import shutil

from typing import Union, overload
from zipfile import ZipFile
from datetime import datetime
from PyQt5.QtCore import QUrl, QRectF, Qt
from PyQt5.QtGui import QPixmap, QPen
from PyQt5.QtWidgets import QFileDialog, QGraphicsRectItem, QListWidgetItem, QComboBox

from database.utils import UtilsForSettings
from images.annotation import Annotation
from images.core import ImageCore
from images.utils import ImageStatus, ARCHIVE_EXTENSION
from label.widget import LabelWidget
from mains.source import Source
from modals.popup.messages import PopupMessages
from modals.popup.utils import Answers


class ImageHandler:
    def __init__(self, connector=None):
        self._connector = connector
        self._images = {}
        self.archive_metadata = {
            "signature": "***REMOVED***",
            "version": 1.0,
            "authorized": "",
            "description": "",
            "date": "",
        }
        self.image_dir_list = []

    @overload
    def add_annotation(self, annotation) -> None: ...
    @overload
    def add_annotation(self, db_item) -> None: ...
    @overload
    def add_annotation(self, source: Source, coords: QRectF, rect_obj: QGraphicsRectItem) -> None: ...
    @overload
    def add_annotation(self, source: Source, coords: QRectF, rect_obj: QGraphicsRectItem, label: str = None) -> None: ...
    def add_annotation(self, **kwargs):
        def add_annotation_index_to_rect():
            # Index text item'ı oluştur
            text_item = self._connector.scene.addText(str(annotation.db_item.annotation_id))
            font = text_item.font()
            font.setPointSize(15)
            font.setBold(True)
            text_item.setFont(font)
            text_item.setDefaultTextColor(Qt.red)
            pixmap = QPixmap(annotation.db_item.image.url)
            img_width = pixmap.width()
            img_height = pixmap.height()

            # Normalize edilmiş koordinatları gerçek koordinatlara çevir
            real_x = (annotation.db_item.x - (annotation.db_item.width/2)) * img_width
            real_y = (annotation.db_item.y - (annotation.db_item.height/2)) * img_height
            
            # Text item'ı rect'in sol üst köşesine yerleştir, biraz offset ile
            text_item.setPos(real_x - 7, 
                    real_y - 27)
            annotation.rect_index = text_item
            widget.annotation_index.setText(str(annotation.db_item.annotation_id))
                
        widget = LabelWidget().setup(self._connector)
        self.fill_label_list(widget.label_list)

        widget.label_list.setCurrentIndex(-1)
        item = QListWidgetItem(self._connector.current_label_list)
        item.setSizeHint(widget.main.sizeHint())
        self._connector.current_label_list.setItemWidget(item, widget.main)

        arg_annotation = kwargs.get("annotation")
        arg_db_item = kwargs.get("db_item")
        arg_source = kwargs.get("source")
        arg_coords = kwargs.get("coords")
        arg_rect_obj = kwargs.get("rect_obj")
        arg_item = kwargs.get("item")
        arg_label = kwargs.get("label")

        
        args = list(kwargs.values())

        if arg_db_item:
            url = QUrl.fromLocalFile(arg_db_item.image.url)
            url.setFragment(arg_db_item.image.main_url)
            annotation = Annotation(
                source=url, 
                coords=(arg_db_item.x, arg_db_item.y, arg_db_item.width, arg_db_item.height), 
                rect_obj=QGraphicsRectItem, 
                item=item, 
                label=arg_db_item.label_id, 
                db_item=arg_db_item)
            self.add_annotation_to_list(annotation)
        elif arg_annotation:
            annotation = args[0]
            annotation.item = item
            if annotation.label is not None:
                widget.label_list.setCurrentIndex(int(annotation.label))
        else:
            if len(args) == 3:
                annotation = Annotation(source=arg_source, coords=arg_coords, rect_obj=arg_rect_obj, item=arg_item if arg_item else item)
            elif len(args) == 4:
                annotation = Annotation(source=arg_source, coords=arg_coords, rect_obj=arg_rect_obj, item=arg_item, label=arg_label)

            image_id = self._connector.database.image.filter(args[0].toLocalFile()).id
            db_item = self._connector.database.annotation.add(
                image_id, 
                annotation.label,
                annotation.coords
            )
            annotation.db_item = db_item

            self.add_annotation_to_list(annotation)
        self.set_dashboard_values()
        add_annotation_index_to_rect()
        self.check_annotation_in_current_source(annotation.source)
        widget.delete_label.clicked.connect(lambda: self.delete_annotation(annotation))
        widget.view_label.clicked.connect(lambda: self.hide(annotation))
        widget.label_list.currentTextChanged.connect(lambda: self.type_changed(widget.label_list.currentText(), annotation))

    def hide(self, annotation):
        if annotation.rect_obj:
            annotation.rect_obj.setVisible(not annotation.rect_obj.isVisible())
        if annotation.rect_index:
            annotation.rect_index.setVisible(not annotation.rect_index.isVisible())

    def delete_annotation(self, annotation, only_front=False):
        if only_front:
            self.delete_all_annotation_from_list()
        else:
            self.delete_one_annotation_from_list(annotation)
            if annotation.rect_obj:
                # Sahneyi al
                scene = self._connector.scene
                
                # Rect'i sahneden sil
                if annotation.rect_obj in scene.items():
                    scene.removeItem(annotation.rect_obj)
                    # Rect'i memory'den temizle
                    annotation.rect_obj = None
                if annotation.rect_index in scene.items():
                    scene.removeItem(annotation.rect_index)
                    annotation.rect_index = None
                
                self.remove_annotation(annotation)
            self.set_dashboard_values()
            self.check_annotation_in_current_source(annotation.source)
            self._connector.authorize_project()


    def delete_all_annotation_from_list(self):
        # Widget'ı listeden bul ve sil
        list_widget = self._connector.current_label_list
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            widget = list_widget.itemWidget(item)
            if widget:
                widget.deleteLater()  # QWidget nesnesini temizle
                widget = None

        # Sonra tüm item'leri temizle
        list_widget.clear()
    
    def delete_one_annotation_from_list(self, annotation):
        # Widget'ı listeden bul ve sil
        list_widget = self._connector.current_label_list
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if item == annotation.item:
                widget = list_widget.itemWidget(item)
                if widget:
                    widget.deleteLater()  # QWidget nesnesini temizle
                    widget = None
                list_widget.takeItem(list_widget.row(item))
    
    def type_changed(self, l_type, annotation):
        for item in self._connector.configurator.label_type:
            if item.name == l_type.split()[-1]:
                annotation.label = item.unique_id
                self._connector.database.annotation.update(db_item=annotation.db_item, label_id=annotation.label)
                self.check_annotation_in_current_source(annotation.source)
                break
        self.set_dashboard_values()
        self._connector.authorize_project()
    
    def add_multi_annotation(self, source: Source):
        self.delete_multi_annotation(source)
        if self.get_annotation(source.current):
            # Görsel boyutlarını al
            pixmap = self._connector.image_pixmap
            annotations = self.get_annotation(source.current).copy()
            for annotation in annotations:
                rect = self.rect_creater_with_coordinate(annotation.coords, pixmap)
                # Scene üzerinde rect oluştur
                pen = QPen(Qt.red, 2)
                annotation.rect_obj = self._connector.scene.addRect(rect, pen)
            
                # Yeni annotation'ı ekle
                self.add_annotation(annotation=annotation)
    
    def delete_multi_annotation(self, source: Source):
        path = False
        if self.get_annotation(source.previous):
            path = source.previous
        elif self.count > 0 and source.previous is None:
            path = source.current
        if path:
            annotations_clear = self.get_annotation(path).copy()
            for annotation in annotations_clear:
                self.delete_annotation(annotation, only_front=True)
    
    def rect_creater_with_coordinate(self, coordinate: tuple, pixmap: QPixmap) -> QRectF:
        img_width = pixmap.width()
        img_height = pixmap.height()

        # Normalize edilmiş koordinatları al
        center_x, center_y, width, height = coordinate
                
        # Gerçek koordinatlara çevir
        real_width = width * img_width
        real_height = height * img_height
        
        # Merkez koordinatlarını sol üst köşe koordinatlarına çevir
        real_x = (center_x * img_width) - (real_width / 2)
        real_y = (center_y * img_height) - (real_height / 2)

        # QRectF ile dikdörtgen oluştur
        return QRectF(real_x, real_y, real_width, real_height)


    def insert_image(self, drop_list=False, route=True):
        temp_list = self._images.copy()
        if drop_list:
            self.insert_from_drag_drop(drop_list)
        else:
            self.insert_from_file_dialog()
        if temp_list != self._images:
            self._connector.database.setting.update("session", True)
            self._connector.show_message(PopupMessages.Info.M102)
            if route:
                if self._connector.pushButton_continue_labeling_from_images.isVisible():
                    self._connector.pages.setCurrentIndex(2)
                else:
                    self._connector.pages.setCurrentIndex(1)
            self._connector.image_table.setCurrentItem(self._connector.image_table.item(0, 1))
            self.set_dashboard_values()
    
    def insert_from_drag_drop(self, drop_list):
        drop_list = self.copy_image_to_temp_dir(drop_list)
        for image in drop_list:
            if image.path().endswith((".png", ".jpg", ".jpeg")) and image not in self._images:
                self.add_image(url=image, read_only=False)

    def insert_from_file_dialog(self):
        selected_list = self.copy_image_to_temp_dir(QFileDialog.getOpenFileNames(self._connector, "Görselleri Uygulamaya Aktar", "", "Images (*.png *.jpg *.jpeg)")[0])
        for image in selected_list:
            if image not in self._images:
                self.add_image(url=image, read_only=False)

    def insert_project(self, drop_list = False):
        """
            Projeyi uygulamaya ekler.

            args:
                drop_list (list): Sürükleyip bırakılan dosyaların listesi.
        """
        if bool(int(self._connector.database.setting.filter(UtilsForSettings.SESSION.value).value)):
            self._connector.show_message(PopupMessages.Warning.M206)
        else:
            if drop_list:
                path = self.insert_project_from_drag_drop(drop_list)
            else:
                path = self.insert_project_from_file_dialog()
            if path:
                with ZipFile(path.toLocalFile(), 'r') as archive:
                    if archive.comment != b"***REMOVED***":
                        self._connector.show_message(PopupMessages.Error.M302)  # Add appropriate error message
                        return
                    archive.extractall(self._connector.database.settings.tempdir)  # Zip dosyasını çıkar
                    name_list = archive.namelist()
                    lbl = list(filter(lambda x: x.endswith('.lbl'), name_list))[0]
                    self._connector.configurator.import_labels(os.path.join(self._connector.database.settings.tempdir, lbl))
                    name_list.remove(lbl)

                    metadata = list(filter(lambda x: x.endswith('metadata.json'), name_list))[0]
                    with open(os.path.join(self._connector.database.settings.tempdir, metadata), 'r') as metadata_file:
                        metadata = json.load(metadata_file)
                        if metadata.get("authorized"):
                            self._connector.authorize_project(metadata.get("authorized"), False)


                    images = list(filter(lambda x: x.lower().endswith(('.png', '.jpg', '.jpeg')), name_list))
                    for image in images:
                        image_path = os.path.join(self._connector.database.settings.tempdir, image)
                        if os.path.exists(image_path):
                            self.add_image(url=QUrl.fromLocalFile(image_path), read_only=False)
                            name_list.remove(image)
                    self._connector.database.setting.update("session", True)
                    self.create_annotations_for_included_past_works(self._connector.database.settings.tempdir, name_list)
                self._connector.pages.setCurrentIndex(2)
                self._connector.load_selected_image(0, 1)
                self.set_dashboard_values()
    
    def insert_project_from_drag_drop(self, drop_list):
        for archive in drop_list:
            if archive.toLocalFile().endswith(ARCHIVE_EXTENSION):
                return archive
    
    def insert_project_from_file_dialog(self):
        selected_file = QFileDialog.getOpenFileName(self._connector, "Çalışmayı Uygulamaya Aktar", "", f"ANNS File (*{ARCHIVE_EXTENSION})")[0]
        if QUrl.fromLocalFile(selected_file).path().endswith(ARCHIVE_EXTENSION):
            return QUrl.fromLocalFile(selected_file)
        
    def insert_from_database(self):
        """

        """
        images = self._connector.database.image.get()
        for image in images:
            url = QUrl.fromLocalFile(image.url)
            url.setFragment(image.main_url)
            self.add_image(url=url)
        if images:
            self._connector.database.setting.update("session", True)

        annotations = self._connector.database.annotation.get()
        for annotation in annotations:
            self.add_annotation(
                db_item=annotation
            )
        self._connector.pages.setCurrentIndex(2)
        self._connector.load_selected_image(0 if images.all() else -1, 1)
        self.set_dashboard_values()
    
    def clear_tempdir(self):
        if os.path.exists(self._connector.database.settings.tempdir):
            for image in os.listdir(self._connector.database.settings.tempdir):
                os.remove(os.path.join(self._connector.database.settings.tempdir, image))
            os.rmdir(self._connector.database.settings.tempdir)

    def create_annotations_for_included_past_works(self, tmpdir, name_list):
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
                            self.add_annotation(source=image, coords=coords, rect_obj=rect_obj, label=int(line[0]))
                            self.check_annotation_in_current_source(image)
        
    def check_image_path_list(self, path: str) -> Union[QUrl, bool]:
        for image in self._images:
            if '.'.join(image.toLocalFile().split("/")[-1].split('.')[:-1]) == path.split("/")[-1].split(".")[0]:
                return image
        if path.endswith('.lbl'):
            return True
        return False

    def check_annotation_in_current_source(self, source: QUrl) -> bool:
        """
            Belirtilen görselin etiket durumunu kontrol eder ve günceller.

            args:
                source (QUrl): Kontrol edilecek görselin kaynağı.
        """
        image_id = self._connector.database.image.filter(source.toLocalFile()).id
        if self._connector.database.annotation.get_by_image_id(image_id):
            state = self._connector.database.annotation.has_none_label(
                image_id=image_id,
            )
            if state:
                state = ImageStatus.UNANNOTATED
            else:
                state = ImageStatus.ANNOTATED
        else:
            state = ImageStatus.UNANNOTATED
        self._images[source].set_status(state)
    
    def export(self):
        """
            Gerekli kontrolleri yaptıktan sonra etiketleri seçili bir dizine aktarır.

            Bu yöntem etiketlerin kullanılabilirliğini ve kaydedilmemiş herhangi bir
            değişiklik olup olmadığını kontrol eder. Etiketler kullanılabilirse ve kullanıcı onaylarsa, kullanıcının
            dışa aktarılan verileri kaydetmek için bir dizin seçmesine izin verir. Dışa aktarma
            başarılıysa, bir başarı mesajı görüntülenir. 
            
            İşlem sırasında herhangi bir hata olması durumunda, hata mesajı gösterilir.
        """
        try:
            available_annotation = self._connector.database.annotation.count()
            defined_annotation = self._connector.database.annotation.defined_count()
            if available_annotation == 0:
                self._connector.show_message(PopupMessages.Warning.M200)
            else:
                if available_annotation - defined_annotation > 0:
                    answer = self._connector.show_message(PopupMessages.Action.M400)
                if available_annotation - defined_annotation == 0 or answer == Answers.OK:
                    save_dir = QFileDialog.getExistingDirectory(self._connector, 'Çalışmanın Kaydedileceği Klasörü Seçin')
                    if save_dir:
                        self.zipper(save_dir)
                        self._connector.show_message(PopupMessages.Info.M101)
        except Exception as _:
            self._connector.show_message(PopupMessages.Error.M301)
    
    def zipper(self, save_dir):
        """
            Bir dizi görüntü için açıklamalar ve meta veriler içeren bi r ZIP arşivi oluşturur.

            Args:
                save_dir (str): ZIP dosyasının kaydedileceği dizin.

            Nots:
            - ZIP dosyası bir UUID kullanılarak adlandırılır ve belirtilen dizine kaydedilir.
        """
        def get_image_name(image):
            # Get local file path from QUrl
            image_path = image.toLocalFile()
            image_name = os.path.basename(image_path)
            base_name = os.path.splitext(image_name)[0]
            return image_path, image_name, base_name
        with ZipFile(os.path.join(save_dir, str(uuid.uuid4()) + ARCHIVE_EXTENSION), 'w') as archive:
            exists_error = False
            for image in self.images:
                try:
                    # Get local file path from QUrl
                    image_path, image_name, base_name = get_image_name(image)
                    
                    # Add the original image file to archive
                    archive.write(image_path, image_name)
                except Exception:
                    exists_error = True
                    continue
            if exists_error:
                self._connector.show_message(PopupMessages.Warning.M203)
            for image in self.images:
                image_path, image_name, base_name = get_image_name(image)
                if os.path.exists(image_path):
                    content = ""
                    for annotation in self.get_annotation(image):
                        if isinstance(annotation.label, int):
                            content += f"{annotation.label} {annotation.coords[0]} {annotation.coords[1]} {annotation.coords[2]} {annotation.coords[3]}\n"
                    if content:
                        archive.writestr(f'{base_name}.txt', content)
            label_type = {}
            for item in self._connector.configurator.label_type:
                label_type[item.name] = item.unique_id
            
            authorized = self._connector.login.user.username if bool(self._connector.database.setting.filter(UtilsForSettings.AUTHORIZED.value).value) else None
            metadata = self.update_metadata(authorized = authorized, date = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            archive.writestr('metadata.json', json.dumps(metadata))
            archive.writestr(str(uuid.uuid4()) + '.lbl', str(label_type))
            archive.comment = b"***REMOVED***"
        archive.close()
    
    @property
    def count(self) -> int:
        """
            Çalışmaya ekli olan görsel sayısını döndürür.

            returns:
                int: Görsel sayısı.
        """
        return len(self._images)
    
    @property
    def images(self):
        """
            Görsel listesini döndürür.

            returns:
                dict: Görsel listesi.
        """
        return self._images
    
    @overload
    def add_annotation_to_list(self, annotation: Annotation) -> None: ...
    @overload
    def add_annotation_to_list(self, annotations: list[Annotation]) -> None: ...
    def add_annotation_to_list(self, *args):
        """
            Görsele etiket ekler.

            args:
                args (Annotation or list[Annotation]): Eklenilecek etiket veya etiketler.
        """
        if args and isinstance(args[0], list):
            for annotation in args[0]:
                self._images[annotation.source].add_annotation(annotation)
        else:
            self._images[args[0].source].add_annotation(args[0])
    
    def get_annotation(self, source: QUrl) -> list:
        if source in self._images:
            return self._images[source]._annotations
        return []
    
    def remove_annotation(self, annotation: Annotation):
        """
            Görselle ilişkili etiketi kaldırır.
        """
        self._images[annotation.source].remove_annotation(annotation)
        self._connector.database.annotation.delete(annotation.db_item)
    
    def get_annotation_count_from_source(self, source: QUrl) -> int:
        """
            Belirtilen görseldeki etiket sayısını döndürür.

            args:
                source (QUrl): Görselin kaynağı.

            returns:
                int: Etiket sayısı.
        """
        if source in self._images:
            return len(self._images[source]._annotations)
        return 0

    def check_directroy(self, path: QUrl):
        if path.fragment() != "":
            dirname = os.path.dirname(path.fragment()).split('/')[-1]
        else:
            dirname = os.path.dirname(path.toLocalFile()).split('/')[-1]
        if dirname not in self.image_dir_list:
            self.image_dir_list.append(dirname)
            text = ', '.join(self.image_dir_list)
            self._connector.label_image_directory.setText(text)
            self._connector.label_image_directory.setToolTip(text)

    def clear(self):
        self.images.clear()
        self.clear_tempdir()
        self.image_dir_list.clear()

    def add_image(self, url: QUrl, read_only: bool = True):
        self._images[url] = ImageCore(self._connector, url)
        if not read_only:
            main_url = None if url.fragment() == "" else url.fragment()
            self._connector.database.image.add(url.toLocalFile(), main_url)

    def delete_image(self, image):
        answer = self._connector.show_message(PopupMessages.Action.M405)
        if answer == Answers.OK:
            db_item = self._connector.database.image.filter(url=image.toLocalFile())
            if db_item.annotations:
                answer = self._connector.show_message(PopupMessages.Action.M406)
                if answer == Answers.OK:
                    for item in db_item.annotations:
                        self._connector.database.annotation.delete(item)
                else:
                    return
            row_index = self.images[image].row_index
            self._connector.database.image.delete(db_item)
            if row_index == self._connector.image_table.currentRow():
                self._connector.load_selected_image(row_index - 1, 1)
                if row_index == 0:
                    return
            self._connector.image_table.removeRow(self.images[image].row_index)
            self._images.pop(image)

            for index, image in enumerate(self._images):
                self._images[image].row_index = index
        self.set_dashboard_values()
    
    def set_dashboard_values(self):
        self._connector.label_total_image_value.setNum(self._connector.database.image.count())
        self._connector.label_total_annotation_value.setNum(self._connector.database.annotation.count())
        self._connector.label_defined_annotation_value.setNum(self._connector.database.annotation.defined_count())

    def copy_image_to_temp_dir(self, images) -> list:
        print(self._connector.database.settings.tempdir)
        temp_images = []
        for image in images:
            source = image.toLocalFile() if isinstance(image, QUrl) else image
            target = os.path.join(self._connector.database.settings.tempdir, os.path.basename(source))
            shutil.copyfile(source, target)
            url = QUrl.fromLocalFile(target)
            url.setFragment(source)
            temp_images.append(url)
        return temp_images

    def update_metadata(self, **kwargs):
        """
            Metadata günceller.
            args:
                kwargs (dict): Güncellenecek metadata anahtar-değer çiftleri.
        """
        for key, value in kwargs.items():
            if key in self.archive_metadata:
                self.archive_metadata[key] = value
        return self.archive_metadata

    def fill_label_list(self, widget):
        """
            Etiket listesini doldurur.
        """
        widget.blockSignals(True)  # Sinyalleri geçici olarak kapat
        current_text = widget.currentText()
        widget.clear()
        for item in self._connector.configurator.labels:
            widget.addItem(f"{item[0]}")
            widget.setItemData(widget.count() - 1, item[0], Qt.ToolTipRole)
        # Eski seçim varsa tekrar seç
        idx = widget.findText(current_text)
        if idx >= 0:
            widget.setCurrentIndex(idx)
        else:
            widget.setCurrentIndex(-1)
        widget.blockSignals(False)  # Sinyalleri tekrar aç

    def update_all_label_comboboxes(self):
        """
        LabelWidget'ların label_list comboboxlarını günceller.
        """
        list_widget = self._connector.current_label_list
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            widget = list_widget.itemWidget(item)
            for child in widget.children():
                if isinstance(child, QComboBox):
                    self.fill_label_list(child)