from PyQt5.QtWidgets import QWidget, QHBoxLayout, QComboBox, QPushButton, QLabel
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap, QFont

class NoScrollComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.isEditable():
            self.lineEdit().installEventFilter(self)

    def wheelEvent(self, event):
        event.ignore()  # Tekerlek hareketini yok say

    def mousePressEvent(self, event):
        # ComboBox'ın boş alanına tıklanırsa
        if self.isEditable() and self.lineEdit().isReadOnly():
            self.showPopup()
        else:
            super().mousePressEvent(event)

    def eventFilter(self, obj, event):
        if obj == self.lineEdit() and event.type() == event.MouseButtonPress:
            self.showPopup()
            return True
        return super().eventFilter(obj, event)
 

class LabelWidget(QWidget):
    def __init__(self):
        super().__init__()

    def setup(self, connector) -> QWidget:
        self.main = QWidget(connector)
        self.main.setStyleSheet("""QPushButton{
            border:none;
            background-color: transparent;
        }
        QComboBox{
            border:none;
            background-color: transparent;
            color: #EEEEEE;
        }
        QComboBox QAbstractItemView {
            background-color: #6086EF;
            border: 1px solid #555;
            selection-color: white; /* Seçili öğenin yazı rengi */
            padding: 5px;
        }
        QComboBox::drop-down {
            width: 24px; /* Açılır ok alanını genişlet */
            border: none;
        }
        QComboBox::down-arrow {
            image: url(:/images/templates/images/down.svg) center center no-repeat;
            width: 22px;
            height: 22px;
        }""")
        self.main.setObjectName("widget")
        self.main.setMinimumSize(QSize(180, 50))
        self.horizontalLayout_2 = QHBoxLayout(self.main)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.annotation_index = QLabel(self.main)
        self.annotation_index.setObjectName("annotation_index")
        self.annotation_index.setMinimumWidth(20)
        self.annotation_index.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(10)
        self.annotation_index.setFont(font)
        self.horizontalLayout_2.addWidget(self.annotation_index)
        self.label_list = NoScrollComboBox(self.main)
        self.label_list.setObjectName("label_list")
        self.label_list.setEditable(True)
        self.label_list.lineEdit().setPlaceholderText("Etiket Seç")
        self.label_list.lineEdit().setReadOnly(True)
        self.label_list.lineEdit().installEventFilter(self.label_list)
        self.label_list.setMinimumSize(QSize(125, 25))
        self.label_list.setMaximumSize(QSize(125, 25))
        self.horizontalLayout_2.addWidget(self.label_list)
        self.widget_2 = QWidget(self.main)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout = QHBoxLayout(self.widget_2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.view_label = QPushButton(self.widget_2)
        self.view_label.setMinimumSize(QSize(25, 25))
        self.view_label.setMaximumSize(QSize(25, 25))
        self.view_label.setCheckable(True)
        self.view_label.setText("")
        icon = QIcon()
        icon.addPixmap(QPixmap(":/images/templates/images/view.svg"), QIcon.Normal, QIcon.Off)
        icon.addPixmap(QPixmap(":/images/templates/images/unview.svg"), QIcon.Normal, QIcon.On)
        self.view_label.setIcon(icon)
        self.view_label.setIconSize(QSize(18, 18))
        self.view_label.setObjectName("view_label")
        self.horizontalLayout.addWidget(self.view_label)
        self.delete_label = QPushButton(self.widget_2)
        self.delete_label.setMinimumSize(QSize(25, 25))
        self.delete_label.setMaximumSize(QSize(25, 25))
        self.delete_label.setText("")
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(":/images/templates/images/delete.svg"), QIcon.Normal, QIcon.Off)
        self.delete_label.setIcon(icon1)
        self.delete_label.setIconSize(QSize(18, 18))
        self.delete_label.setObjectName("delete_label")
        self.horizontalLayout.addWidget(self.delete_label)
        self.horizontalLayout_2.addWidget(self.widget_2, 0, Qt.AlignRight)

        return self