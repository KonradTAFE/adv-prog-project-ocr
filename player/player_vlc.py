import tkinter as tk
from tkinter import filedialog, messagebox
import vlc
import platform


class VideoPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Video Player")
        self.root.geometry("800x600")

        # VLC instance and player
        self.instance = vlc.Instance('--no-xlib')
        self.player = self.instance.media_player_new()

        # Top control frame
        control_frame = tk.Frame(root)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # File selection button
        tk.Button(control_frame, text="Open Local File",
                  command=self.open_file).pack(side=tk.LEFT, padx=5)

        # URL entry
        tk.Label(control_frame, text="URL:").pack(side=tk.LEFT, padx=5)
        self.url_entry = tk.Entry(control_frame, width=40)
        self.url_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(control_frame, text="Load URL",
                  command=self.load_url).pack(side=tk.LEFT, padx=5)

        # Video frame
        self.video_frame = tk.Frame(root, bg="black")
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Playback controls
        playback_frame = tk.Frame(root)
        playback_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(playback_frame, text="Play",
                  command=self.play).pack(side=tk.LEFT, padx=5)
        tk.Button(playback_frame, text="Pause",
                  command=self.pause).pack(side=tk.LEFT, padx=5)
        tk.Button(playback_frame, text="Stop",
                  command=self.stop).pack(side=tk.LEFT, padx=5)
        tk.Button(playback_frame, text="Capture Frame",
                  command=self.capture_frame).pack(side=tk.LEFT, padx=20)

        # Embed VLC player in the frame
        ## self.embed_video()

    def embed_video(self):
        """Embed VLC player into the Tkinter window"""
        if platform.system() == "Windows":
            self.player.set_hwnd(self.video_frame.winfo_id())
        elif platform.system() == "Linux":
            self.player.set_xwindow(self.video_frame.winfo_id())
        elif platform.system() == "Darwin":  # macOS
            # Wait for window to be fully realized
            self.root.update()
            self.player.set_nsobject(self.video_frame.winfo_id())

    def open_file(self):
        """Open a local video file"""
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mkv *.mov *.flv *.wmv"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.load_media(file_path)

    def load_url(self):
        """Load video from URL"""
        url = self.url_entry.get().strip()
        if url:
            self.load_media(url)
        else:
            messagebox.showwarning("Warning", "Please enter a URL")

    def load_media(self, path):
        """Load media from file path or URL"""
        try:
            media = self.instance.media_new(path)
            self.player.set_media(media)
            self.embed_video()  # Move here instead of __init__
            self.play()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load media: {str(e)}")

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
            snapshot_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")]
            )
            if snapshot_path:
                # video_take_snapshot(num, path, width, height)
                # 0 for default size
                self.player.video_take_snapshot(0, snapshot_path, 0, 0)
                messagebox.showinfo("Success", f"Frame saved to:\n{snapshot_path}")
        else:
            messagebox.showwarning("Warning", "No video playing")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoPlayer(root)
    root.mainloop()

