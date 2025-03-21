import ast

from PyQt5.QtWidgets import QListWidgetItem, QFileDialog



class Configurator(object):
    def __init__(self, connector=None):
        self._connector = connector
        self.label_type = []


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
            self.label_type.append({len(self.label_type): text})
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
                for label in self.label_type:
                    f.write(f"{label}\n")

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
                for line in f:
                    text = ast.literal_eval(line.strip())
                    if text:
                        item = QListWidgetItem(text[len(self.label_type)])
                        self._connector.listWidget_label_list.addItem(item)
                        self.label_type.append(text)

    