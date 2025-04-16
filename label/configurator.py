import ast
from typing import overload

from PyQt5.QtWidgets import QListWidgetItem, QFileDialog

from modals.popup.messages import PopupMessages
from modals.popup.utils import Answers
from label.utils import LABEL_TYPES



class Configurator(object):
    def __init__(self, connector=None):
        self._connector = connector
        self.label_type = {}
        self.clear()
    
    @property
    def labels(self):
        return self.label_type.keys()

    def clear(self):
        self.label_type = LABEL_TYPES
        self._connector.listWidget_label_list.clear()
        for lbl in self.label_type.keys():
            item = QListWidgetItem(lbl)
            self._connector.listWidget_label_list.addItem(item)

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
        if text in self.label_type.keys():
            self._connector.show_message(PopupMessages.Warning.M202)
        else:
            if text != '':
                self.label_type[text] = len(self.label_type)
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

    