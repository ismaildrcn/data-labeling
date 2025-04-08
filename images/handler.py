import os
import tempfile

from typing import Union
from zipfile import ZipFile

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QFileDialog, QGraphicsRectItem

from images.core import ImageCore
from images.utils import ImageStatus


class ImageHandler:
    def __init__(self, connector=None):
        self._connector = connector
        self.images = {}

    def insert(self, drop_list=False):
        old_working = False
        if drop_list:
            self.insert_from_drag_drop(old_working, drop_list)
        else:
            old_working = self.insert_from_file_dialog(old_working)
        self.insert_old_working(old_working)
        if self.images:
            self._connector.pages.setCurrentIndex(1)
            self._connector.image_table.setCurrentItem(self._connector.image_table.item(0, 1))
        old_working = False
    
    def insert_from_drag_drop(self, old_working, drop_list):
        for image in drop_list:
            if image.path().endswith((".png", ".jpg", ".jpeg")) and image not in self.images:
                self.images[image] = ImageCore(self._connector, image)
            elif image.path().endswith(".zip"):
                old_working = image
        return old_working

    def insert_from_file_dialog(self, old_working: bool):
        selected_list = QFileDialog.getOpenFileNames(self._connector, "Görselleri Uygulamaya Aktar", "", "Images (*.png *.jpg *.jpeg, *.zip)")[0]
        for image in selected_list:
            if image.endswith(".zip"):
                old_working = QUrl.fromLocalFile(image)
            elif QUrl.fromLocalFile(image) not in self.images:
                self.images[QUrl.fromLocalFile(image)] = ImageCore(self._connector, QUrl.fromLocalFile(image))
        return old_working
    
    def insert_old_working(self, path: Union[QUrl, bool]):
        if path:
            with tempfile.TemporaryDirectory() as tmpdir:
                with ZipFile(path.toLocalFile(), 'r') as archive:
                    archive.extractall(tmpdir)  # Zip dosyasını çıkar
                    name_list = archive.namelist()
                    lbl = list(filter(lambda x: x.endswith('.lbl'), name_list))[0]
                    self._connector.configurator.import_labels(tmpdir + '/' + lbl)
                    name_list.remove(lbl)
                    self.create_annotations_for_included_past_works(tmpdir, name_list)
                    for item in archive.namelist():
                        os.remove(tmpdir + '/' + item)

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
                            self._connector.annotations.add(image, coords, rect_obj, int(line[0]))
        
    def check_image_path_list(self, path: str) -> Union[QUrl, bool]:
        for image in self.images:
            if '.'.join(image.toLocalFile().split("/")[-1].split('.')[:-1]) == path.split("/")[-1].split(".")[0]:
                return image
        if path.endswith('.lbl'):
            return True
        return False

    def check_annotation_in_current_source(self, source: QUrl) -> bool:
        state = ImageStatus.ANNOTATED
        if source in self._connector.annotations.annotation_dict:
            for annotation in self._connector.annotations.annotation_dict[source]:
                if annotation.label == None:
                    state = ImageStatus.UNANNOTATED
                    break
        self.images[source].set_status(state)