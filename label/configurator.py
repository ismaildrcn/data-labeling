import ast
from typing import overload

from PyQt5.QtWidgets import QListWidgetItem, QFileDialog, QTableWidgetItem, QPushButton, QWidget, QHBoxLayout, QAbstractItemView
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from modals.popup.messages import PopupMessages
from modals.popup.utils import Answers
from label.utils import LABEL_TYPES

from database.models.label.model import Label
SETTINGS = {}

class Configurator(object):
    def __init__(self, connector=None):
        self._connector = connector
        
        # Table widget setup
        self._connector.tableWidget_label_list.setColumnCount(2)
        self._connector.tableWidget_label_list.setColumnWidth(0, 40)  # Delete button column
        self._connector.tableWidget_label_list.setColumnWidth(1, 350) # Label column
        self._connector.tableWidget_label_list.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.label_type = {}
        for key, value in LABEL_TYPES.items():
            self._connector.database.label.add(name=key, is_default=True)
        self.add_default_labels()                
    
    @property
    def labels(self):
        labels = self._connector.database.label.get().all()
        self.get_settings_from_database()
        if bool(int(SETTINGS['use_default_labels'])):
            return [[label.name, label.unique_id + 1] for label in labels]
        else:
            return [[label.name, label.unique_id + 1] for label in labels if not label.is_default]
        

    def reset(self):
        """
            Etiket listesini varsayılan etiketlerle sıfırlar.

            Bu method, etiket listesini varsayılan etiketlerle doldurur
            ve etiket listesi widget'ını günceller.

            Returns:
                None
        """
        self._connector.tableWidget_label_list.clear()
        # Add default labels
        self.add_default_labels()
        self._connector.database.setting.update('use_default_labels', True)
        
    def add_default_labels(self):
        """
        Varsayılan etiketleri ekler.
        Default etiketler için silme butonu olmayacak.
        """
        self.label_type = self._connector.database.label.get().all()
        self._connector.tableWidget_label_list.setRowCount(0)
        
        for label in self.label_type:
            self.create_table_item_for_label(label)

    def delete_label(self, name):
        """
        Etiket silme işlemi.
        Label ismi üzerinden silme işlemi yapar.
        
        Args:
            name (str): Silinecek etiketin ismi
        """
        # Database'den label objesini bul
        label = next((lbl for lbl in self.label_type if lbl.name == name), None)
        
        if label and not label.is_default:
            # Database'den sil
            self._connector.database.label.delete(label)
            
            # Tablodan bul ve sil
            items = self._connector.tableWidget_label_list.findItems(name, Qt.MatchExactly)
            if items:
                row = items[0].row()
                self._connector.tableWidget_label_list.removeRow(row)
            
            # Memory'den sil
            self.label_type = [lbl for lbl in self.label_type if lbl.name != name]

    def add(self):
        """
        Yeni bir etiket ekler.
        Yeni eklenen etiketler için silme butonu ekler.
        """
        text = self._connector.lineEdit_add_label.text()
        name_list = [item for item in self.label_type if item.name == text]
        if name_list:
            self._connector.show_message(PopupMessages.Warning.M202)
        else:
            if text != '':
                db_item = self._connector.database.label.add(name=text, is_default=False)
                self.label_type.append(db_item)
                self.create_table_item_for_label(db_item)
                self._connector.lineEdit_add_label.clear()
                
    def export_labels(self):
        """
            Etiketleri bir dosyaya dışa aktarır.

            Bu method, oluşturulan etiket listesini (.lbl) uzantılı bir dosyaya kaydeder.
            Kullanıcı bir dosya konumu ve ismi seçmek için dosya kaydetme dialog penceresi açılır.
            Her etiket, dosyaya ayrı bir satır olarak kaydedilir.

            Returns:
                None
        """
        if not self.label_type:
            self._connector.show_message(PopupMessages.Warning.M201)
            return
        fname = QFileDialog.getSaveFileName(self._connector, 'Etiketleri Bilgisayara Aktar', '', 'Label Files (*.lbl)')[0]
        if fname:
            temp = {}
            for label in self.label_type:
                temp[label.name] = label.unique_id
            with open(fname, 'w') as f:
                f.write(str(temp))

    @overload
    def import_labels(self) -> None: ...
    @overload
    def import_labels(self, file_path: str) -> None: ...
    def import_labels(self, *args):
        """
        Etiketleri bir dosyadan içe aktarın ve etiket listesine ekleyin.

        Bu fonksiyon, kullanıcının bir etiket dosyası seçmesi için bir dosya iletişim kutusu açar,
        dosyanın içeriğini okur ve her etiketi etiket listesine ve tabloya ekler.

        Args:
            *args: Opsiyonel dosya yolu

        Returns:
            None
        """
        if not args and self.label_type:
            answer = self._connector.show_message(PopupMessages.Action.M401)
        else:
            answer = Answers.OK
            
        if answer == Answers.OK:
            self.label_type.clear()
            self._connector.tableWidget_label_list.setRowCount(0)
            
            if args:
                fname = args[0]
            else:
                fname = QFileDialog.getOpenFileName(
                    self._connector, 
                    'Etiketleri Uygulamaya Aktar', 
                    '', 
                    'Label Files (*.lbl)'
                )[0]
                
            if fname:
                with open(f"{fname}", 'r') as f:
                    text = ast.literal_eval(f.readline().strip())
                    if text:
                        for key, value in text.items():
                            # Database'e ekle veya var olanı al
                            if not self._connector.database.label.filter(Label.name, key):
                                db_item = self._connector.database.label.add(name=key, is_default=False)
                            else:
                                db_item = self._connector.database.label.filter(Label.name, key)[0]
                            self.label_type.append(db_item)
                            
                            self.create_table_item_for_label(db_item)

    def get_settings_from_database(self):
        """
            Ayarları alır.

            Bu method, ayarları veritabanından alır ve
            etiket listesi widget'ını günceller.

            Returns:
                None
        """
        settings = self._connector.database.setting.get().all()
        for setting in settings:
            SETTINGS[setting.name] = setting.value

    def create_table_item_for_label(self, label):
        """
            Etiket için tablo öğesi oluşturur.

            Args:
                label (str): Etiket ismi
        """
        row = self._connector.tableWidget_label_list.rowCount()
        self._connector.tableWidget_label_list.insertRow(row)
        
        if not label.is_default:
            # Create widget for centered button
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            
            # Delete button
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon(":/images/templates/images/delete.svg"))
            delete_btn.setFixedSize(22, 22)
            delete_btn.clicked.connect(lambda checked, name=label.name: self.delete_label(name))
            
            # Add button to layout centered
            btn_layout.addWidget(delete_btn, 0, Qt.AlignCenter)
            
            # Set widget as cell widget
            self._connector.tableWidget_label_list.setCellWidget(row, 0, btn_widget)
        
        # Label name item
        name_item = QTableWidgetItem(label.name)
        self._connector.tableWidget_label_list.setItem(row, 1, name_item)
        self._connector.tableWidget_label_list.scrollToBottom()