from PyQt5.QtWidgets import QListWidgetItem, QFileDialog

import ast


class Labels(object):
    def __init__(self, connector=None):
        self._connector = connector
        self.label_list = []


    def add(self):
        text = self._connector.lineEdit_add_label.text()
        if text != '':
            self.label_list.append({len(self.label_list): text})
            print(self.label_list)
            item = QListWidgetItem(text)
            self._connector.listWidget_label_list.addItem(item)
            self._connector.lineEdit_add_label.clear()

    def export_labels(self):
        if not self.label_list:
            print("No labels to export.")
            return
        fname = QFileDialog.getSaveFileName(self._connector, 'Export Labels', '', 'Label Files (*.lbl)')[0]
        if fname:
            with open(f"{fname}.lbl", 'w') as f:
                for label in self.label_list:
                    f.write(f"{label}\n")

    def import_labels(self):
        self.label_list.clear()
        fname = QFileDialog.getOpenFileName(self._connector, 'Insert Labels', '', 'Label Files (*.lbl)')[0]
        if fname:
            with open(f"{fname}", 'r') as f:
                for line in f:
                    text = ast.literal_eval(line.strip())
                    if text:
                        item = QListWidgetItem(text[len(self.label_list)])
                        self._connector.listWidget_label_list.addItem(item)
                        self.label_list.append(text)
        print(self.label_list)
