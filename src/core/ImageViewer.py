from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel, QPushButton, QFileDialog
)

from .pyreddit_downloader import RedditImageDownloader
import httpx

class ImageViewer(QWidget):

    def __init__(self, post_id: str, downloader: RedditImageDownloader) -> None:
        super().__init__(None)
        images = downloader.get_images(post_id)
        
        self.setMinimumSize(300, 400)

        self.lay = QVBoxLayout()
        self.title = QLabel(f"Images for {post_id}")
        self.title.setAlignment(Qt.AlignCenter)
        self.lay.addWidget(self.title)
        
        for img in images:
            tmp_lay = QVBoxLayout()
            w = QLabel()
            data = self.get_img_data(img.thumbnail)
            pixm = QPixmap(data).scaled(300, 300, Qt.KeepAspectRatio)
            w.setPixmap(pixm)
            tmp_lay.addWidget(w)

            down_btn = QPushButton("Download")
            down_btn.clicked.connect(lambda : self.download_image(img.url))
            tmp_lay.addWidget(down_btn)
            
            self.lay.addLayout(tmp_lay)

            
        self.setLayout(self.lay)

    def get_img_data(self, url: str) -> bytes:
        with httpx.Client() as client:
            resp = client.get(url)
            return resp.content
        
    def download_image(self, url):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Image Files (*.png *.jpg)")
        if filename:
            with open(filename, "wb") as f:
                f.write(self.get_img_data(url))