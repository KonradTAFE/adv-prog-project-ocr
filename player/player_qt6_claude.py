import sys
import json
import platform
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLineEdit, QLabel,
                             QFileDialog, QMessageBox, QFrame, QComboBox)
from PyQt6.QtCore import Qt
import vlc


class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyclops Video Player")
        self.setGeometry(100, 100, 800, 600)

        # VLC instance and player
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Load config
        self.config_path = self.get_config_path()
        self.recent_items = self.load_recent_items()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Recent items dropdown
        recent_layout = QHBoxLayout()
        recent_layout.addWidget(QLabel("Recent:"))
        self.recent_combo = QComboBox()
        self.recent_combo.addItem("-- Select recent file or URL --")
        self.recent_combo.addItems(self.recent_items)
        self.recent_combo.currentTextChanged.connect(self.on_recent_selected)
        recent_layout.addWidget(self.recent_combo)
        layout.addLayout(recent_layout)

        # Top control layout
        control_layout = QHBoxLayout()

        # File selection button
        open_btn = QPushButton("Open Local File")
        open_btn.clicked.connect(self.open_file)
        control_layout.addWidget(open_btn)

        # URL entry
        control_layout.addWidget(QLabel("URL:"))
        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText("Paste URL here (including YouTube links)")
        self.url_entry.returnPressed.connect(self.load_url)
        control_layout.addWidget(self.url_entry)

        load_url_btn = QPushButton("Load URL")
        load_url_btn.clicked.connect(self.load_url)
        control_layout.addWidget(load_url_btn)

        layout.addLayout(control_layout)

        # Video frame
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("background-color: black;")
        self.video_frame.setMinimumSize(640, 480)
        layout.addWidget(self.video_frame)

        # Playback controls
        playback_layout = QHBoxLayout()

        play_btn = QPushButton("Play")
        play_btn.clicked.connect(self.play)
        playback_layout.addWidget(play_btn)

        pause_btn = QPushButton("Pause")
        pause_btn.clicked.connect(self.pause)
        playback_layout.addWidget(pause_btn)

        stop_btn = QPushButton("Stop")
        stop_btn.clicked.connect(self.stop)
        playback_layout.addWidget(stop_btn)

        playback_layout.addStretch()

        capture_btn = QPushButton("Capture Frame")
        capture_btn.clicked.connect(self.capture_frame)
        playback_layout.addWidget(capture_btn)

        layout.addLayout(playback_layout)

    def get_config_path(self):
        """Get platform-appropriate config file path"""
        if platform.system() == "Darwin":  # macOS
            config_dir = Path.home() / "Library" / "Application Support" / "Cyclops"
        elif platform.system() == "Windows":
            import os
            config_dir = Path(os.environ.get('APPDATA', Path.home())) / "Cyclops"
        else:  # Linux
            config_dir = Path.home() / ".config" / "cyclops"

        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.json"

    def load_recent_items(self):
        """Load recent files/URLs from config"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('recent_items', [])
        except Exception as e:
            print(f"Error loading config: {e}")
        return []

    def save_recent_items(self):
        """Save recent files/URLs to config"""
        try:
            config = {'recent_items': self.recent_items}
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def add_to_recent(self, path):
        """Add item to recent list (max 10 items)"""
        # Remove if already exists
        if path in self.recent_items:
            self.recent_items.remove(path)

        # Add to front
        self.recent_items.insert(0, path)

        # Keep only last 10
        self.recent_items = self.recent_items[:10]

        # Update combo box
        self.recent_combo.clear()
        self.recent_combo.addItem("-- Select recent file or URL --")
        self.recent_combo.addItems(self.recent_items)

        # Save to config
        self.save_recent_items()

    def on_recent_selected(self, text):
        """Handle selection from recent items dropdown"""
        if text and text != "-- Select recent file or URL --":
            self.load_media(text)

    def showEvent(self, event):
        """Embed VLC player after window is shown"""
        super().showEvent(event)
        if not hasattr(self, '_embedded'):
            self._embedded = True
            self.embed_video()

    def embed_video(self):
        """Embed VLC player into the Qt window"""
        if platform.system() == "Darwin":  # macOS
            self.player.set_nsobject(int(self.video_frame.winId()))
        elif platform.system() == "Windows":
            self.player.set_hwnd(int(self.video_frame.winId()))
        elif platform.system() == "Linux":
            self.player.set_xwindow(int(self.video_frame.winId()))

    def open_file(self):
        """Open a local video file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video files (*.mp4 *.avi *.mkv *.mov *.flv *.wmv);;All files (*.*)"
        )
        if file_path:
            self.load_media(file_path)

    def load_url(self):
        """Load video from URL"""
        url = self.url_entry.text().strip()
        if url:
            self.load_media(url)
        else:
            QMessageBox.warning(self, "Warning", "Please enter a URL")

    def load_media(self, path):
        """Load media from file path or URL"""
        try:
            media = self.instance.media_new(path)
            self.player.set_media(media)
            self.add_to_recent(path)
            self.play()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load media: {str(e)}")

    def play(self):
        """Play the video"""
        self.player.play()

    def pause(self):
        """Pause the video"""
        self.player.pause()

    def stop(self):
        """Stop the video"""
        self.player.stop()

    def capture_frame(self):
        """Capture current frame as image"""
        if self.player.is_playing() or self.player.get_state() == vlc.State.Paused:
            # Pause if playing
            was_playing = self.player.is_playing()
            if was_playing:
                self.pause()

            # Take snapshot
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Frame",
                "",
                "PNG files (*.png);;JPEG files (*.jpg)"
            )
            if file_path:
                # video_take_snapshot(num, path, width, height)
                # 0 for default size
                self.player.video_take_snapshot(0, file_path, 0, 0)
                QMessageBox.information(self, "Success", f"Frame saved to:\n{file_path}")
        else:
            QMessageBox.warning(self, "Warning", "No video playing")

    def closeEvent(self, event):
        """Clean up VLC player on close"""
        self.player.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())