from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy, QSpacerItem
from PySide6.QtGui import QMouseEvent, QKeyEvent, Qt, QPixmap
from PySide6.QtCore import Signal

from .NListWidget import NListWidget
from .Notifier import Post
from .ImageViewer import ImageViewer

DEFAULT_STYLE_SHEET = """
QFrame {
    border-radius: 10px;
    background-color: #2d2d2d;
}
QFrame:hover {
    background-color: #414040;
}
"""
DEFAULT_LABEL_STYLE = """
QLabel {
    color: #999797;
    font-size: 15px;
    background-color: transparent;
    font-family: Roboto;
    word-wrap: 
}
"""

class ListItem(QFrame):
    
    clicked = Signal(type)
    instances = 0

    def __init__(self, parent: NListWidget, text: str, description: str, icon_pixmap: QPixmap, post: Post, downloader):
        super().__init__(parent)
        ListItem.instances += 1 # increment counter

        self.list_view = parent
        self.text = text
        self.post = post
        self.icon_pixmap = icon_pixmap
        self.img_downloader = downloader

        self.is_selected = False

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Setup Layout for custom ListItem
        self.mainVlay = QVBoxLayout()

        self.layout = QHBoxLayout()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Set the size policy of the widget

        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignCenter)
        # height for each box
        self.setContentsMargins(0, 0, 0, 0)
        
        self.setStyleSheet(DEFAULT_STYLE_SHEET)

        # Icon side
        img_lay = QVBoxLayout()
        img_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel()
        icon.setStyleSheet(DEFAULT_LABEL_STYLE + "border-radius: 5px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_pixmap = self.icon_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon.setPixmap(self.icon_pixmap)
        img_lay.addWidget(icon)

        if len(self.text) > 40:
            text = self.text[:40] + '...'

        # text setup
        self.text_frame = QFrame()
        self.text_frame.setStyleSheet("background-color: transparent;")
        self.text_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.text_layout = QVBoxLayout()
        self.text_layout.setSpacing(4)
        self.text_frame.setLayout(self.text_layout)
            
        top_text_layout = QHBoxLayout()
        top_text_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        title = QLabel(text.strip())
        title.setStyleSheet(DEFAULT_LABEL_STYLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flair = QLabel(post.flair or "No Flair")
        flair.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignCenter)
        flair.setStyleSheet(f"""
            background-color: {post.link_flair_background_color or "gray"};
            border-radius: 5px;
            color: white;
            padding: 4px;
            font-weight: bold;
            font-size: 12px;
        """)
        flair.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        flair.adjustSize()
        date_text = QLabel(post.last_post_date.strftime("%m/%d, %I:%M %p"))    
        date_text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        date_text.setStyleSheet(DEFAULT_LABEL_STYLE)      

        top_text_layout.addWidget(title)
        top_text_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        top_text_layout.addWidget(flair)

        if len(description) > 100:
            description = description[:100] + '...'

        desc = QLabel(description)
        desc.setAlignment(Qt.AlignmentFlag.AlignLeft)
        desc.setWordWrap(True)
        desc.setStyleSheet(DEFAULT_LABEL_STYLE)

        self.text_layout.addLayout(top_text_layout)
        self.text_layout.addWidget(desc)
        self.text_layout.addWidget(date_text, alignment=Qt.AlignmentFlag.AlignRight)
        self.layout.addLayout(img_lay)
        self.layout.addWidget(self.text_frame)

        subreddit_lbl = QLabel("r/" + post.subreddit_name)
        subreddit_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subreddit_lbl.setStyleSheet("background-color: transparent; color: white; font-weight: semibold; font-size: 14px; margin-bottom: 4px;")
        subreddit_lbl.font().setPointSize(14)

        self.mainVlay.addWidget(subreddit_lbl)
        self.mainVlay.addLayout(self.layout)
        self.setLayout(self.mainVlay)


    @classmethod
    def get_index(cls):
        return cls.instances -1 # return the current value of the counter for the class

    def select_item(self):
        """Deselect all other items and select this item"""
        # remove other selection/s
        self.list_view.reset_selection()
        # update selected on current item
        self.set_selected(True)
        # update selected on list view
        self.list_view.set_selected_index(ListItem.get_index())

    def set_selected(self, value: bool):
        self.is_selected = value
        
        if value:
            self.setStyleSheet("QWidget { background-color: #404258; }" + DEFAULT_STYLE_SHEET)
        else:
            self.setStyleSheet(DEFAULT_STYLE_SHEET)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Enter:
            self.clicked.emit(self)
        return super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self)

    def open_image_viewer(self, event: QMouseEvent):
        raise NotImplementedError
        if event.button() == Qt.MouseButton.LeftButton:
            self.viewer = ImageViewer(self.post.idstr, self.img_downloader)
            self.viewer.show()