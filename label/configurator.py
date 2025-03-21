import ast

from PyQt5.QtWidgets import QListWidgetItem, QFileDialog



class Configurator(object):
    def __init__(self, connector=None):
        self._connector = connector
        self.label_type = {}
    
    @property
    def labels(self):
        return self.label_type.keys()
        


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
            print("No labels to export.")
            return
        fname = QFileDialog.getSaveFileName(self._connector, 'Export Labels', '', 'Label Files (*.lbl)')[0]
        if fname:
            with open(f"{fname}.lbl", 'w') as f:
                f.write(str(self.label_type))

    def import_labels(self):
        """
            Etiketleri bir dosyadan içe aktarın ve etiket listesine ekleyin.

            Bu fonksiyon, kullanıcının bir etiket dosyası seçmesi için bir dosya iletişim kutusu açar,
            dosyanın içeriğini okur ve her etiketi etiket listesine
            ve QListWidget'a ekler.

            Returns:
                None
        """
        self.label_type.clear()
        fname = QFileDialog.getOpenFileName(self._connector, 'Insert Labels', '', 'Label Files (*.lbl)')[0]
        if fname:
            with open(f"{fname}", 'r') as f:
                text = ast.literal_eval(f.readline().strip())
                if text:
                    for lbl in text:
                        item = QListWidgetItem(lbl)
                        self._connector.listWidget_label_list.addItem(item)
                self.label_type = text

    