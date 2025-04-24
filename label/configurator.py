import ast
from typing import overload

from PyQt5.QtWidgets import QListWidgetItem, QFileDialog

from modals.popup.messages import PopupMessages
from modals.popup.utils import Answers
from label.utils import LABEL_TYPES

from database.models.label.model import Label
SETTINGS = {}

class Configurator(object):
    def __init__(self, connector=None):
        self._connector = connector
        self.label_type = {}
        for key, value in LABEL_TYPES.items():
            self._connector.database.label.add(unique_id=value, name=key, is_default=True)
        self.add_default_labels()                
    
    @property
    def labels(self):
        labels = self._connector.database.label.get().all()
        self.get_settings_from_database()
        if bool(int(SETTINGS['use_default_labels'])):
            return [[label.name, label.unquie_id + 1] for label in labels]
        else:
            return [[label.name, label.unquie_id + 1] for label in labels if not label.is_default]
        

    def reset(self):
        """
            Etiket listesini varsayılan etiketlerle sıfırlar.

            Bu method, etiket listesini varsayılan etiketlerle doldurur
            ve etiket listesi widget'ını günceller.

            Returns:
                None
        """
        # Clear the current label list
        not_default_labels = self._connector.database.label.filter(Label.is_default, False)
        for label in not_default_labels:
            self._connector.database.label.delete(label)
        self._connector.listWidget_label_list.clear()
        # Add default labels
        self.add_default_labels()
        self._connector.database.setting.update('use_default_labels', True)
        
    def add_default_labels(self):
        """
            Varsayılan etiketleri ekler.

            Bu method, varsayılan etiketleri etiket listesine ekler
            ve etiket listesi widget'ını günceller.

            Returns:
                None
        """
        self.label_type = self._connector.database.label.get().all()
        for lbl in self.label_type:
            item = QListWidgetItem(lbl.name)
            self._connector.listWidget_label_list.addItem(item)
        self._connector.database.setting.update('use_default_labels', True)
        

    def clear(self):
        """
            Etiket listesini temizler.

            Bu method, etiket listesini sıfırlar ve etiket listesi
            widget'ını temizler.

            Returns:
                None
        """
        if self.label_type:
            answer = self._connector.show_message(PopupMessages.Action.M403)
            if answer is Answers.OK:
                labels = self._connector.database.label.get().all()
                for label in labels:
                    if not label.is_default:
                        self._connector.database.label.delete(label)
                self._connector.listWidget_label_list.clear()
            self._connector.database.setting.update('use_default_labels', False)

    def add(self):
        """
            Yeni bir etiket ekler.

            Bu method, kullanıcının girdiği metni etiket olarak ekler.
            Etiket text input alanından alınır ve hem etiket listesine
            hem de görsel listeye eklenir.

            Returns:
                None
        """
        text = self._connector.lineEdit_add_label.text()
        name_list  = [item for item in self.label_type if item.name == text]
        if text in name_list:
            self._connector.show_message(PopupMessages.Warning.M202)
        else:
            if text != '':
                db_item = self._connector.database.label.add(unique_id=len(self.label_type), name=text, is_default=False)
                self.label_type.append(db_item)
                item = QListWidgetItem(text)
                self._connector.listWidget_label_list.addItem(item)
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
            with open(fname, 'w') as f:
                f.write(str(self.label_type))

    @overload
    def import_labels(self) -> None: ...
    @overload
    def import_labels(self, file_path: str) -> None: ...
    def import_labels(self, *args):
        """
            Etiketleri bir dosyadan içe aktarın ve etiket listesine ekleyin.

            Bu fonksiyon, kullanıcının bir etiket dosyası seçmesi için bir dosya iletişim kutusu açar,
            dosyanın içeriğini okur ve her etiketi etiket listesine
            ve QListWidget'a ekler.

            Returns:
                None
        """
        if self.label_type:
            answer = self._connector.show_message(PopupMessages.Action.M401)
        else:
            answer = Answers.OK
        if answer == Answers.OK:
            self.label_type.clear()
            self._connector.listWidget_label_list.clear()
            if args:
                fname = args[0]
            else:
                fname = QFileDialog.getOpenFileName(self._connector, 'Etiketleri Uygulamaya Aktar', '', 'Label Files (*.lbl)')[0]
            if fname:
                with open(f"{fname}", 'r') as f:
                    text = ast.literal_eval(f.readline().strip())
                    if text:
                        for lbl in text:
                            item = QListWidgetItem(lbl)
                            self._connector.listWidget_label_list.addItem(item)
                    self.label_type = text

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