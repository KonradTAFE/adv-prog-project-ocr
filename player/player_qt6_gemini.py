"""
player_qt6_gemini.py
Myk: Mike Holland, J336025, from 4/11/2025

"""

import sys

from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView
import vlc

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cross-Platform Video Player")

        # Main widget and layout
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        # URL input bar
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter video URL or file path")
        self.layout.addWidget(self.url_input)

        # Play button
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.play_video)
        self.layout.addWidget(self.play_btn)

        # Embedded browser for navigating to video URLs (including YouTube)
        self.browser = QWebEngineView()
        self.layout.addWidget(self.browser, 2)

        # VLC player instance
        self.vlc_instance = vlc.Instance()
        self.media_player = self.vlc_instance.media_player_new()

        # Video widget for VLC video output
        self.video_frame = QWidget()
        self.video_frame.setMinimumHeight(400)
        self.layout.addWidget(self.video_frame, 3)

        # Link VLC video output to the video_frame widget
        if sys.platform.startswith('linux'):
            self.media_player.set_xwindow(self.video_frame.winId())
        elif sys.platform == 'win32':
            self.media_player.set_hwnd(self.video_frame.winId())
        elif sys.platform == 'darwin':
            self.media_player.set_nsobject(int(self.video_frame.winId()))

    def play_video(self):
        video_source = self.url_input.text()
        if not video_source:
            return
        if video_source.startswith("http"):  # URL: open in embedded browser and play with VLC
            self.browser.load(QUrl(video_source))   ## TODO: fix type. Need QUrl or QWebEngineHttpRequest
        # Set VLC media to the URL or local file
        media = self.vlc_instance.media_new(video_source)
        self.media_player.set_media(media)
        self.media_player.play()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())
