import os
import sys
from PySide6.QtCore import Qt, QRect, QTimer
from PySide6.QtGui import QIcon, QPixmap, QFont, QAction
from PySide6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QSystemTrayIcon, 
    QMenu,
    QFrame, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QMessageBox, QToolTip, QWidget
)
import requests
import webbrowser

from core.NListWidget import NListWidget
from core.ListItem import ListItem
from core.Notifier import Notifier, Post
from core.Settings import SettingsWindow
from core.pyreddit_downloader import RedditImageDownloader
from core import conf

import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Notificaiton Thread definition
        # self.notifier = None
        self.notifiers = []

        # Create a system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_img = QIcon(conf.ICON_FILE)
        self.tray_icon.setIcon(self.tray_img)
        self.tray_icon.setVisible(True)
        self.tray_icon.setToolTip("Reddit Notifier")
        self.tray_icon.activated.connect(self.on_tray_icon_clicked)
        
        # Create a context menu for the system tray icon
        self.tray_menu = QMenu(self)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.on_exit_action_triggered)
        self.tray_menu.addAction(exit_action)
        self.tray_icon.setContextMenu(self.tray_menu)
       

        # Setup Window
        self.setFixedSize(430, 650)
        self.setWindowTitle("Reddit Notifier")
        self.setWindowIcon(self.tray_img)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon("icons/icon.ico"))

        # fonts
        self.header_font = QFont("Menlo", 24)
        self.header2_font = QFont("Menlo", 18)

        self.setup_layouts()

        setitngs_page = SettingsWindow()
        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.setStyleSheet("background-color: #232323;")

        self.stacked_widget.addWidget(self.frame)
        self.stacked_widget.addWidget(setitngs_page)
        self.setCentralWidget(self.stacked_widget)

        file_abs_path = os.path.join(os.path.dirname(__file__), "style.qss") # the absolute path of the file with 
        with open(file_abs_path, "r") as style:
            self.setStyleSheet(style.read())

        if conf.has_valid_config():
            self.set_up_notifier() # start listening
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Reddit Notifier")
            msg.setText("Please configure the application first.")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.Ok)
            if msg.exec() == QMessageBox.Ok:
                self.stacked_widget.setCurrentIndex(1)
                return
            else:
                # exit
                QApplication.quit()
                sys.exit()

        self.img_downloader = RedditImageDownloader()

        self.hide()

    def close_all_notifiers(self):
        for notifier in self.notifiers:
            notifier.terminate()
            notifier.wait()
        
    def set_up_notifier(self):
        try:
            config = conf.config()
            subreddit = conf.parse_subreddits(config)

            for sub in subreddit:
                notifier = Notifier(
                    subred=sub,
                    user=config.get(conf.USER_SECTION, conf.USER_USERNAME, raw=True),
                    passw=config.get(conf.USER_SECTION, conf.USER_PASS, raw=True),
                    client_id=config.get(conf.CLIENT_SECTION, conf.CLIENT_ID, raw=True),
                    client_secret=config.get(conf.CLIENT_SECTION, conf.CLIENT_SECRET, raw=True),

                    # settings
                    retry_delay=config.getint(conf.SETTINGS_SECTION, conf.SETTINGS_DELAY, raw=True)
                )
                notifier.postFound.connect(self.post_found)
                notifier.fetchFailed.connect(self.fetch_failed)
                notifier.start()
                self.notifiers.append(notifier)

        except Exception as e:
            print(e)
            QMessageBox.critical(self, "Error", f"An error occurred while setting up the notifier.\n{str(e)}")
            QApplication.quit()
            sys.exit()

    def fetch_failed(self, title, msg):
        self.close_all_notifiers()
        QMessageBox.critical(self, title, msg)
        QApplication.quit()
        sys.exit(-1)

    def setup_layouts(self):
        self.frame = QFrame()
        self.frame.setContentsMargins(8, 10, 8, 10)
        self.frame.setStyleSheet("""
            background-color: #232323;
            margin: 0;
            padding: 0;
        """)
        self.layout = QVBoxLayout()
        self.frame.setLayout(self.layout)

        self.list_view = NListWidget()

        # Top bar contents
        self.top_bar = QHBoxLayout()

        self.settings_btn = QPushButton()      
        self.settings_btn.setIcon(QPixmap("icons/setting.png"))  
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.clicked.connect(self.on_settings_btn_clicked)

        self.time_status = QLabel("Notifier")
        self.time_status.setFont(self.header2_font)
        self.time_status.setStyleSheet("color: #999797; font-size: 20px;")

        self.top_bar.addWidget(self.time_status, alignment=Qt.AlignmentFlag.AlignLeft)
        self.top_bar.addWidget(self.settings_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.layout.setSpacing(20)
        self.layout.addLayout(self.top_bar)
        self.layout.addWidget(self.list_view)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # self.setCentralWidget(self.frame)

    def on_settings_btn_clicked(self):
        self.stacked_widget.setCurrentIndex(1)

    def add_test_data(self):
        import datetime
        for _ in range(10):
            p = Post("322", "tester_man_390", "Test Data " * 10, ".wdawd", "PAID", "red", datetime.datetime.now(), "https://google.com/icon.png")
            list_item = ListItem(self.list_view, "teste", "Hello, i need a few bitches edited, so they look like they have been sold to slavery and back, can anyone do it? i pay well!", QPixmap("icons/icon.png"), p)
            self.list_view.add_list_item(list_item, self.list_item_clicked)

    def post_found(self, post: Post):
        pixm = QPixmap()
        if post.thumbnail_url and post.thumbnail_url != "default":
            try: 
                imgr = requests.get(post.thumbnail_url)
                if imgr.ok:
                    pixm.loadFromData(imgr.content)
                else:
                    pixm.load(conf.ICON_FILE)
            except requests.exceptions.MissingSchema:
                pixm.load(conf.ICON_FILE)
        else:
            pixm.load(conf.ICON_FILE)

        list_item = ListItem(self.list_view, post.author, post.title, pixm, post, self.img_downloader)
        self.list_view.add_list_item(list_item, self.list_item_clicked)
        self.tray_icon.showMessage(
            f"{post.subreddit_name}, {post.author} - {post.flair}", 
            post.title, 
            icon=QSystemTrayIcon.MessageIcon.NoIcon, 
            msecs=1000
        )
        app = QApplication.instance()
        app.processEvents()
        self.tray_icon.messageClicked.connect(lambda : self.on_tray_icon_clicked(QSystemTrayIcon.Trigger))

    def list_item_clicked(self, item: ListItem):
        webbrowser.open(item.post.link)

    def on_tray_icon_clicked(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.showNormal()
            self.activateWindow()
    
    def closeEvent(self, event):
        # Minimize the main window to the system tray when it is closed
        event.ignore()
        self.hide()

    def show_custom_notification(self, title, message):
        # icon = QIcon(icon_path)
        # pixmap = icon.pixmap(32, 32)  # Adjust size as needed
        
        html_content = f"""
        <table>
            <tr>
                <td style="padding-left: 10px;">
                    <b>{title}</b><br>{message}
                </td>
            </tr>
        </table>
        """
        
        QToolTip.showText(
            self.tray_icon.geometry().topRight(),
            html_content,
            msecShowTime=4000  # Display for 3 seconds
        )
    
    def on_exit_action_triggered(self):
        self.close_all_notifiers()
        self.tray_icon.hide()
        QApplication.quit()
        exit(0)

if __name__ == "__main__":
    # init config
    conf.init()

    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontUseNativeMenuBar)
    window = MainWindow()
    screen_size = app.primaryScreen().availableGeometry()
    window.setGeometry(QRect(screen_size.width() - 450, screen_size.height() - 670, 400, 300))
    window.show()
    sys.exit(app.exec())