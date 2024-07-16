from PySide6.QtCore import Qt, QCoreApplication, QProcess
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QSpinBox,
    QFrame,
    QListWidget,
    QInputDialog,
    QListWidgetItem
)

import sys
from . import conf

class MList(QWidget):
    def __init__(self, items):
        super().__init__()
        self.items = items
        self.initUI()

    def initUI(self):
        mainLayout = QHBoxLayout()
        self.setMaximumHeight(120)
        self.setMinimumHeight(120)

        # List Widget
        self.listWidget = QListWidget()
        self.listStyleSheet = """
            QListWidget::item {
                padding: 4px;
            }
            QListWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }
        """
        self.listWidget.setStyleSheet(self.listStyleSheet)
        self.listWidget.selectionChanged = self.listItemChanged
        for item_str in self.items:
            item = QListWidgetItem(item_str)
            self.listWidget.addItem(item)
            self.listWidget.setCurrentItem(item)

        # Buttons
        buttonStyle = """
        padding: 10px;
        background-color: #6aa1ff;
        color: white;
        font-size: 18px;
        font-weight: 500;
        border-radius: 5px;
        """
        buttonLayout = QVBoxLayout()
        addButton = QPushButton("+")
        addButton.setStyleSheet(buttonStyle)
        removeButton = QPushButton("-")
        removeButton.setStyleSheet(buttonStyle)
        
        addButton.clicked.connect(self.addItem)
        removeButton.clicked.connect(self.removeItem)
        
        buttonLayout.addWidget(addButton)
        buttonLayout.addWidget(removeButton)
        buttonLayout.addStretch()
        
        mainLayout.addWidget(self.listWidget)
        mainLayout.addLayout(buttonLayout)
        
        self.setLayout(mainLayout)

    def listItemChanged(self, *_):
        if self.listWidget.currentRow() == 0:
            self.listWidget.setStyleSheet(self.listStyleSheet  + """
            QListWidget::item:selected {
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            """)
        else:
            self.listWidget.setStyleSheet(self.listStyleSheet)

    def addItem(self):
        text, ok = QInputDialog.getText(self, "Add Item", "Enter new item:")
        if ok and text:
            item = QListWidgetItem(text)
            self.listWidget.addItem(item)
            self.listWidget.setCurrentItem(item)

    def removeItem(self):
        for item in self.listWidget.selectedItems():
            self.listWidget.takeItem(self.listWidget.row(item))

    def getAllItems(self):
        return [self.listWidget.item(i) for i in range(self.listWidget.count())]

class SettingsWindow(QWidget):

    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.INPUT_STYLES = "font-size: 14px; color: white; padding: 10px; border-radius: 10px;"
        self.BUTTON_STYLES = """
            background-color: #6aa1ff;
            color: white;
            font-size: 18px;
            font-weight: 500;
            padding: 10px;
            border-radius: 10px;
        """
        self.setContentsMargins(2, 2, 2, 2)
        self.lay = QVBoxLayout()
        self.lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.title_bar = QHBoxLayout()

        self.back_btn = self.create_button("", QPixmap("icons/back.png"), callback=self.go_home)
        self.title = QLabel("Settings")
        self.title.setStyleSheet("background-color: transparent; color: white; font-size: 24px;")        
        self.title_bar.addWidget(self.back_btn)
        self.title_bar.addWidget(self.title, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        
        config = conf.config()
        self.subreddits_list = MList(conf.parse_subreddits(config))

        self.username_field = self.create_input("Username")
        self.username_field.setText(config.get(conf.USER_SECTION, conf.USER_USERNAME, fallback=""))

        self.password_field = self.create_input("Password", QLineEdit.EchoMode.Password)
        self.password_field.setText(config.get(conf.USER_SECTION, conf.USER_PASS, fallback=""))

        self.client_id_field = self.create_input("Client ID", QLineEdit.EchoMode.Password)
        self.client_id_field.setText(config.get(conf.CLIENT_SECTION, conf.CLIENT_ID, fallback=""))

        self.client_id_secret = self.create_input("Client Secret", QLineEdit.EchoMode.Password)
        self.client_id_secret.setText(config.get(conf.CLIENT_SECTION, conf.CLIENT_SECRET, fallback=""))

        self.check_interval = self.create_spinbox(25, 200, config.getint(conf.SETTINGS_SECTION, conf.SETTINGS_DELAY, fallback=25))
        self.check_interval.setSuffix(" sec")
        self.save_btn = self.create_button("Save And Restart", callback=self.save_all)

        # laying it out
        self.lay.addLayout(self.title_bar)
        
        self.lay.addWidget(self.create_label("Subreddits"))
        self.lay.addWidget(self.subreddits_list)
        # self.lay.addWidget(self.subreddit_field)
        self.lay.addWidget(self.get_seperator())
        self.lay.addWidget(self.create_label("User"))
        self.lay.addWidget(self.username_field)
        self.lay.addWidget(self.password_field)
        self.lay.addWidget(self.get_seperator())
        self.lay.addWidget(self.create_label("Client"))
        self.lay.addWidget(self.client_id_field)
        self.lay.addWidget(self.client_id_secret)
        self.lay.addWidget(self.get_seperator())
        self.lay.addWidget(self.create_label("Check Interval"))
        self.lay.addWidget(self.check_interval)


        self.lay.addWidget(self.save_btn, alignment=Qt.AlignmentFlag.AlignBottom)
        ################


        self.setLayout(self.lay)

        self.setStyleSheet("""
            background-color: #2d2d2d;
        """)

    def subreddit_names_to_str(self):
        items = self.subreddits_list.getAllItems()
        return ",".join([item.text() for item in items])

    def go_home(self):
        self.parent().parent().stacked_widget.setCurrentIndex(0)

    def create_input(self, placeholder: str, echo_mode: QLineEdit.EchoMode = QLineEdit.EchoMode.Normal):
        input_widget = QLineEdit()
        input_widget.setPlaceholderText(placeholder)
        input_widget.setMinimumHeight(25)
        input_widget.setStyleSheet(self.INPUT_STYLES)
        input_widget.setEchoMode(echo_mode)
        return input_widget
    
    def create_button(self, text: str, icon: QPixmap = None, callback = None):
        button = QPushButton(text)
        button.clicked.connect(callback)
        if icon:
            button.setIcon(icon)
            button.setStyleSheet("background-color: transparent; padding: 0; margin: 0;")
        else:
            button.setMinimumHeight(25)
            button.setStyleSheet(self.BUTTON_STYLES)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button
    
    def create_label(self, text: str):
        label = QLabel(text)
        label.setStyleSheet("background-color: transparent; color: white; font-size: 18px;")
        return label
    
    def create_spinbox(self, min_: int, max_: int, value: int):
        spinbox = QSpinBox()
        spinbox.setMinimum(min_)
        spinbox.setMaximum(max_)
        spinbox.setValue(value)
        spinbox.setStyleSheet(self.INPUT_STYLES)
        spinbox.setCursor(Qt.CursorShape.PointingHandCursor)
        return spinbox
    
    def get_seperator(self):
        Separador = QFrame()
        Separador.setFrameShape(QFrame.HLine)
        Separador.setFrameShadow(QFrame.Sunken)
        return Separador

    def save_all(self):
        conf.init() # create file if doesnt exists
        config = conf.config()

        config.set(conf.SUBREDDITS_SECTION, conf.SUBREDDIT_NAMES, self.subreddit_names_to_str())
        config.set(conf.USER_SECTION, conf.USER_USERNAME, self.username_field.text())
        config.set(conf.USER_SECTION, conf.USER_PASS, str(self.password_field.text()))
        config.set(conf.CLIENT_SECTION, conf.CLIENT_ID, self.client_id_field.text())
        config.set(conf.CLIENT_SECTION, conf.CLIENT_SECRET, self.client_id_secret.text())
        config.set(conf.SETTINGS_SECTION, conf.SETTINGS_DELAY, str(self.check_interval.value()))
        
        conf.save_config(config)
        
        # restart
        if self.parent().parent().notifiers:
            self.parent().parent().close_all_notifiers()

        QCoreApplication.quit()
        status = QProcess.startDetached(sys.executable, sys.argv)
        print(status)