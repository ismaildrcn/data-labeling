import os

from typing import Union, overload
import uuid
from zipfile import ZipFile

from PyQt5.QtCore import QUrl, QRectF, Qt
from PyQt5.QtGui import QPixmap, QPen
from PyQt5.QtWidgets import QFileDialog, QGraphicsRectItem, QListWidgetItem

from images.annotation import Annotation
from images.core import ImageCore
from images.utils import ImageStatus, TEMPDIR, ARCHIVE_EXTENSION
from label.widget import LabelWidget
from mains.source import Source
from modals.popup.messages import PopupMessages
from modals.popup.utils import Answers

from database.utils import Tables


class ImageHandler:
    def __init__(self, connector=None):
        self._connector = connector
        self._images = {}
        self.annotation_count = 0

    @overload
    def add_annotation(self, annotation) -> None: ...
    @overload
    def add_annotation(self, source: Source, coords: QRectF, rect_obj: QGraphicsRectItem) -> None: ...
    @overload
    def add_annotation(self, source: Source, coords: QRectF, rect_obj: QGraphicsRectItem, label: str = None) -> None: ...
    def add_annotation(self, *args):
        widget = LabelWidget().setup(self._connector)
        for item in self._connector.configurator.labels:
            widget.label_list.addItem(f"{item[1]} - {item[0]}")
            widget.label_list.setItemData(widget.label_list.count() - 1, item[0], Qt.ToolTipRole)

        widget.label_list.setCurrentIndex(-1)
        item = QListWidgetItem(self._connector.current_label_list)
        item.setSizeHint(widget.main.sizeHint())
        self._connector.current_label_list.setItemWidget(item, widget.main)

        if len(args) != 1:
            if len(args) == 3:
                annotation = Annotation(args[0], args[1], args[2], item)
            elif len(args) == 4:
                annotation = Annotation(args[0], args[1], args[2], item, args[3])

            self.annotation_count += 1
            self.add_annotation_to_list(annotation)
        else:
            annotation = args[0]
            annotation.item = item
            if annotation.label is not None:
                widget.label_list.setCurrentIndex(int(annotation.label))

        widget.delete_label.clicked.connect(lambda: self.delete_annotation(annotation))
        widget.view_label.clicked.connect(lambda: self.hide(annotation))
        widget.label_list.currentTextChanged.connect(lambda: self.type_changed(widget.label_list.currentText(), annotation))

    def hide(self, annotation):
        if annotation.rect_obj:
            annotation.rect_obj.setVisible(not annotation.rect_obj.isVisible())

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
                self.remove_annotation(annotation)
                self.annotation_count -= 1
            _, _, defined_label_count = self.check_annotation
            self._connector.label_defined_annotation_value.setText(str(defined_label_count))
            self.check_annotation_in_current_source(annotation.source)

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
            if item.name == l_type:
                annotation.label = item.unquie_id
                self.check_annotation_in_current_source(annotation.source)
                break
        _, _, defined_label_count = self.check_annotation
        self._connector.label_defined_annotation_value.setText(str(defined_label_count))
        
    @property
    def check_annotation(self):
        defined_label_count = 0
        available_annotation = False
        has_unwrite = False
        for image in self.images:
            for annotation in self.get_annotation(image):
                if annotation.label is None:
                    has_unwrite = True
                else:
                    defined_label_count += 1
                available_annotation = True
        return has_unwrite, available_annotation, defined_label_count

    
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
                self.add_annotation(annotation)
    
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


    def insert_image(self, drop_list=False):
        if drop_list:
            self.insert_from_drag_drop(drop_list)
        else:
            self.insert_from_file_dialog()
        if self._images:
            self._connector.pages.setCurrentIndex(1)
            self._connector.image_table.setCurrentItem(self._connector.image_table.item(0, 1))
            _, _, defined_ann = self.check_annotation
            self._connector.label_defined_annotation_value.setText(str(defined_ann))
    
    def insert_from_drag_drop(self, drop_list):
        for image in drop_list:
            if image.path().endswith((".png", ".jpg", ".jpeg")) and image not in self._images:
                self._images[image] = ImageCore(self._connector, image)
                self._connector.database.image.add(image.toLocalFile())

    def insert_from_file_dialog(self):
        selected_list = QFileDialog.getOpenFileNames(self._connector, "Görselleri Uygulamaya Aktar", "", "Images (*.png *.jpg *.jpeg)")[0]
        for image in selected_list:
            if QUrl.fromLocalFile(image) not in self._images:
                self._images[QUrl.fromLocalFile(image)] = ImageCore(self._connector, QUrl.fromLocalFile(image))
                self._connector.database.image.add(image)

    def insert_project(self, drop_list = False):
        if drop_list:
            path = self.insert_project_from_drag_drop(drop_list)
        else:
            path = self.insert_project_from_file_dialog()
        if path:
            with ZipFile(path.toLocalFile(), 'r') as archive:
                if archive.comment != b"***REMOVED***":
                    self._connector.show_message(PopupMessages.Error.M302)  # Add appropriate error message
                    return
                archive.extractall(TEMPDIR)  # Zip dosyasını çıkar
                name_list = archive.namelist()
                lbl = list(filter(lambda x: x.endswith('.lbl'), name_list))[0]
                self._connector.configurator.import_labels(os.path.join(TEMPDIR, lbl))
                name_list.remove(lbl)

                images = list(filter(lambda x: x.lower().endswith(('.png', '.jpg', '.jpeg')), name_list))
                for image in images:
                    image_path = os.path.join(TEMPDIR, image)
                    if os.path.exists(image_path):
                        self._images[QUrl.fromLocalFile(image_path)] = ImageCore(self._connector, QUrl.fromLocalFile(image_path))
                        name_list.remove(image)

                self.create_annotations_for_included_past_works(TEMPDIR, name_list)
            self._connector.pages.setCurrentIndex(2)
            self._connector.load_selected_image(0, 1)
            _, _, defined_label_count = self.check_annotation
            self._connector.label_defined_annotation_value.setText(str(defined_label_count))
    
    def insert_project_from_drag_drop(self, drop_list):
        for archive in drop_list:
            if archive.toLocalFile().endswith(ARCHIVE_EXTENSION):
                return archive
    
    def insert_project_from_file_dialog(self):
        selected_file = QFileDialog.getOpenFileName(self._connector, "Çalışmayı Uygulamaya Aktar", "", f"ANNS File (*{ARCHIVE_EXTENSION})")[0]
        if QUrl.fromLocalFile(selected_file).path().endswith(ARCHIVE_EXTENSION):
            return QUrl.fromLocalFile(selected_file)
    
    def clear_tempdir(self):
        if os.path.exists(TEMPDIR):
            for image in os.listdir(TEMPDIR):
                os.remove(os.path.join(TEMPDIR, image))

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
                            self.add_annotation(image, coords, rect_obj, int(line[0]))
                            self.check_annotation_in_current_source(image)
        
    def check_image_path_list(self, path: str) -> Union[QUrl, bool]:
        for image in self._images:
            if '.'.join(image.toLocalFile().split("/")[-1].split('.')[:-1]) == path.split("/")[-1].split(".")[0]:
                return image
        if path.endswith('.lbl'):
            return True
        return False

    def check_annotation_in_current_source(self, source: QUrl) -> bool:
        state = ImageStatus.ANNOTATED
        annotations = self.get_annotation(source)
        if annotations:
            for annotation in annotations:
                if annotation.label == None:
                    state = ImageStatus.UNANNOTATED
                    break
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
            has_unwrite, available_annotation, _ = self.check_annotation
            if available_annotation is False:
                self._connector.show_message(PopupMessages.Warning.M200)
            else:
                if has_unwrite:
                    answer = self._connector.show_message(PopupMessages.Action.M400)
                if has_unwrite is False or answer == Answers.OK:
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
            archive.writestr(str(uuid.uuid4()) + '.lbl', str(self._connector.configurator.label_type))
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

    @property
    def annotation_count(self):
        return self._annotation_count
    
    @annotation_count.setter
    def annotation_count(self, value):
        self._annotation_count = value
        self._connector.label_total_annotation_value.setText(str(value))