from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog,
    QListWidget, QSlider, QHBoxLayout, QToolBar, QFrame, QGraphicsDropShadowEffect,
    QSpacerItem, QSizePolicy, QProgressBar, QComboBox, QCheckBox, QGroupBox
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QAudioDevice, QMediaDevices
from PyQt6.QtMultimedia import QMediaDevices, QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, QUrl, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QPalette, QColor, QFont, QAction, QIcon, QPainter, QPen, QBrush
import sys, os, random, math

class AudioVisualizerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(80)
        self.bars = [random.randint(5, 60) for _ in range(32)]
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_bars)
        self.is_playing = False
        
    def start_visualization(self):
        self.is_playing = True
        self.timer.start(50)
        
    def stop_visualization(self):
        self.is_playing = False
        self.timer.stop()
        self.bars = [5] * 32
        self.update()
        
    def update_bars(self):
        if self.is_playing:
            for i in range(len(self.bars)):
                self.bars[i] = max(5, self.bars[i] + random.randint(-15, 15))
                self.bars[i] = min(60, self.bars[i])
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        bar_width = width // len(self.bars) - 2
        
        for i, height in enumerate(self.bars):
            x = i * (bar_width + 2)
            y = self.height() - height
            
            if height > 40:
                painter.setBrush(QBrush(QColor("#ff6b6b")))
            elif height > 25:
                painter.setBrush(QBrush(QColor("#4ecdc4")))
            else:
                painter.setBrush(QBrush(QColor("#45b7d1")))
                
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(x, y, bar_width, height, 2, 2)

class ModernButton(QPushButton):
    def __init__(self, text="", icon_path=""):
        super().__init__()
        self.setText(text)
        self.icon_path = icon_path
        self.setMinimumSize(50, 50)
        self.setMaximumSize(80, 80)
        
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(32, 32))
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

class MediaPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neon Media Player Pro")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)

        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        
        self.audio_output.setVolume(0.7)
        
        self.player.setAudioOutput(self.audio_output)

        self.video_widget = QVideoWidget(self)
        self.player.setVideoOutput(self.video_widget)

        self.playlist = []
        self.current_index = -1
        self.is_fullscreen = False
        self.current_theme = "dark"

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_time_slider)

        self.visualizer = AudioVisualizerWidget()

        self.shuffle_enabled = False
        self.shuffled_indices = []
        self.repeat_mode = 0
        self.is_muted = False
        self.previous_volume = 70

        self.create_ui()
        self.apply_theme("dark")
        
        self.player.playbackStateChanged.connect(self.on_playback_state_changed)
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.player.errorOccurred.connect(self.on_error_occurred)

    def create_ui(self):
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🎧 Neon Media Player Pro")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #4ecdc4; margin: 10px;")
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark Theme", "Light Theme", "Neon Theme"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        self.theme_combo.setMaximumWidth(150)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        theme_icon = QLabel()
        if os.path.exists("icon_theme.png"):
            theme_icon.setPixmap(QIcon("icon_theme.png").pixmap(QSize(20, 20)))
        header_layout.addWidget(theme_icon)
        header_layout.addWidget(self.theme_combo)

        self.track_info_frame = QFrame()
        self.track_info_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        
        track_info_layout = QVBoxLayout()
        
        self.current_track_label = QLabel("🎶 No media loaded")
        self.current_track_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.current_track_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.artist_label = QLabel("Select a file to start playing")
        self.artist_label.setFont(QFont("Segoe UI", 10))
        self.artist_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        track_info_layout.addWidget(self.current_track_label)
        track_info_layout.addWidget(self.artist_label)
        self.track_info_frame.setLayout(track_info_layout)

        self.video_frame = QFrame()
        video_layout = QVBoxLayout()
        video_layout.addWidget(self.video_widget)
        
        self.fullscreen_btn = ModernButton("⛶")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        self.fullscreen_btn.setMaximumSize(40, 40)
        
        video_controls = QHBoxLayout()
        video_controls.addStretch()
        video_controls.addWidget(self.fullscreen_btn)
        
        video_layout.addLayout(video_controls)
        self.video_frame.setLayout(video_layout)

        self.visualizer_frame = QFrame()
        visualizer_layout = QVBoxLayout()
        visualizer_layout.addWidget(QLabel("🎵 Audio Visualizer"))
        visualizer_layout.addWidget(self.visualizer)
        self.visualizer_frame.setLayout(visualizer_layout)

        progress_layout = QVBoxLayout()
        
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setRange(0, 0)
        self.time_slider.sliderMoved.connect(self.seek_position)
        
        time_info_layout = QHBoxLayout()
        self.current_time_label = QLabel("00:00")
        self.total_time_label = QLabel("00:00")
        
        time_info_layout.addWidget(self.current_time_label)
        time_info_layout.addStretch()
        time_info_layout.addWidget(self.total_time_label)
        
        progress_layout.addWidget(self.time_slider)
        progress_layout.addLayout(time_info_layout)

        controls_layout = QHBoxLayout()
        controls_layout.addStretch()
        
        self.shuffle_btn = ModernButton("", "icon_shuffle.png")
        self.prev_btn = ModernButton("", "icon_previous.png")
        self.play_btn = ModernButton("", "icon_play.png")
        self.next_btn = ModernButton("", "icon_next.png")
        self.repeat_btn = ModernButton("", "icon_repeat.png")
        
        self.play_btn.setMinimumSize(70, 70)
        self.play_btn.setMaximumSize(70, 70)
        if os.path.exists("icon_play.png"):
            self.play_btn.setIcon(QIcon("icon_play.png"))
            self.play_btn.setIconSize(QSize(40, 40))
        
        self.shuffle_btn.clicked.connect(self.toggle_shuffle)
        self.prev_btn.clicked.connect(self.prev_media)
        self.play_btn.clicked.connect(self.toggle_play)
        self.next_btn.clicked.connect(self.next_media)
        self.repeat_btn.clicked.connect(self.toggle_repeat)
        
        controls_layout.addWidget(self.shuffle_btn)
        controls_layout.addWidget(self.prev_btn)
        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.next_btn)
        controls_layout.addWidget(self.repeat_btn)
        controls_layout.addStretch()

        speed_layout = QHBoxLayout()
        
        self.speed_icon_btn = QPushButton()
        self.speed_icon_btn.setMaximumSize(30, 30)
        if os.path.exists("icon_speed.png"):
            self.speed_icon_btn.setIcon(QIcon("icon_speed.png"))
            self.speed_icon_btn.setIconSize(QSize(20, 20))
        else:
            self.speed_icon_btn.setText("🚀")
        
        speed_layout.addWidget(self.speed_icon_btn)
        
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(25, 200)
        self.speed_slider.setValue(100)
        self.speed_slider.setMaximumWidth(150)
        self.speed_slider.valueChanged.connect(self.change_speed)
        
        self.speed_label = QLabel("1.0x")
        self.speed_label.setMinimumWidth(40)
        
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_label)
        speed_layout.addStretch()

        volume_layout = QHBoxLayout()
        
        self.volume_icon_btn = QPushButton()
        self.volume_icon_btn.setMaximumSize(30, 30)
        self.volume_icon_btn.clicked.connect(self.toggle_mute)
        if os.path.exists("icon_audio_on.png"):
            self.volume_icon_btn.setIcon(QIcon("icon_audio_on.png"))
            self.volume_icon_btn.setIconSize(QSize(20, 20))
        
        volume_layout.addWidget(self.volume_icon_btn)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(150)
        self.audio_output.setVolume(0.7)
        self.volume_slider.valueChanged.connect(self.change_volume)
        
        self.volume_label = QLabel("70%")
        self.volume_label.setMinimumWidth(40)
        
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_label)
        volume_layout.addStretch()

        audio_device_layout = QHBoxLayout()
        device_icon = QLabel()
        if os.path.exists("icon_output.png"):
            device_icon.setPixmap(QIcon("icon_output.png").pixmap(QSize(20, 20)))
        audio_device_layout.addWidget(device_icon)
        
        self.audio_device_combo = QComboBox()
        self.populate_audio_devices()
        self.audio_device_combo.currentTextChanged.connect(self.change_audio_device)
        self.audio_device_combo.setMaximumWidth(200)
        
        audio_device_layout.addWidget(self.audio_device_combo)
        audio_device_layout.addStretch()

        file_ops_layout = QHBoxLayout()
        
        self.open_file_btn = QPushButton("Open File")
        if os.path.exists("icon_open_file.png"):
            self.open_file_btn.setIcon(QIcon("icon_open_file.png"))
            self.open_file_btn.setIconSize(QSize(20, 20))
        
        self.open_folder_btn = QPushButton("Open Folder")
        if os.path.exists("icon_open_folder.png"):
            self.open_folder_btn.setIcon(QIcon("icon_open_folder.png"))
            self.open_folder_btn.setIconSize(QSize(20, 20))
        
        self.clear_playlist_btn = QPushButton("Clear Playlist")
        if os.path.exists("icon_clear.png"):
            self.clear_playlist_btn.setIcon(QIcon("icon_clear.png"))
            self.clear_playlist_btn.setIconSize(QSize(20, 20))
        
        self.open_file_btn.clicked.connect(self.open_file)
        self.open_folder_btn.clicked.connect(self.open_folder)
        self.clear_playlist_btn.clicked.connect(self.clear_playlist)
        
        file_ops_layout.addWidget(self.open_file_btn)
        file_ops_layout.addWidget(self.open_folder_btn)
        file_ops_layout.addWidget(self.clear_playlist_btn)
        file_ops_layout.addStretch()

        playlist_layout = QVBoxLayout()
        
        playlist_header = QHBoxLayout()
        playlist_label = QLabel("Playlist")
        if os.path.exists("icon_playlist.png"):
            playlist_icon_label = QLabel()
            playlist_icon_label.setPixmap(QIcon("icon_playlist.png").pixmap(QSize(20, 20)))
            playlist_header.addWidget(playlist_icon_label)
        playlist_header.addWidget(playlist_label)
        playlist_header.addStretch()
        
        playlist_layout.addLayout(playlist_header)
        
        self.track_list = QListWidget()
        self.track_list.itemDoubleClicked.connect(self.track_selected)
        
        playlist_layout.addWidget(self.track_list)

        audio_options_layout = QVBoxLayout()
        
        self.visualizer_check = QCheckBox("Show Audio Visualizer")
        self.visualizer_check.setChecked(True)
        self.visualizer_check.toggled.connect(self.toggle_visualizer)
        
        audio_options_layout.addWidget(self.visualizer_check)

        left_panel = QVBoxLayout()
        left_panel.addLayout(header_layout)
        left_panel.addWidget(self.track_info_frame)
        left_panel.addWidget(self.video_frame)
        left_panel.addWidget(self.visualizer_frame)
        left_panel.addLayout(progress_layout)
        left_panel.addLayout(controls_layout)
        left_panel.addLayout(speed_layout)
        left_panel.addLayout(volume_layout)
        left_panel.addLayout(audio_device_layout)
        left_panel.addLayout(file_ops_layout)
        left_panel.addLayout(audio_options_layout)

        right_panel = QVBoxLayout()
        right_panel.addLayout(playlist_layout)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_panel, 3)
        main_layout.addLayout(right_panel, 1)

        self.setLayout(main_layout)

        self.player.positionChanged.connect(self.update_time_display)
        self.player.durationChanged.connect(self.set_duration)
        self.player.mediaStatusChanged.connect(self.handle_media_finished)

    def populate_audio_devices(self):
        self.audio_device_combo.clear()
        
        audio_devices = QMediaDevices.audioOutputs()
        
        for device in audio_devices:
            self.audio_device_combo.addItem(device.description(), device)
        
        default_device = QMediaDevices.defaultAudioOutput()
        if default_device:
            for i in range(self.audio_device_combo.count()):
                if self.audio_device_combo.itemData(i) == default_device:
                    self.audio_device_combo.setCurrentIndex(i)
                    break

    def change_audio_device(self):
        current_device = self.audio_device_combo.currentData()
        if current_device:
            self.audio_output.setDevice(current_device)
            print(f"Audio output changed to: {current_device.description()}")

    def change_speed(self, value):
        speed = value / 100.0
        self.speed_label.setText(f"{speed:.2f}x")
        self.player.setPlaybackRate(speed)
        print(f"Playback speed changed to: {speed}x")

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        
        if theme_name == "dark":
            self.apply_dark_theme()
        elif theme_name == "light":
            self.apply_light_theme()
        elif theme_name == "neon":
            self.apply_neon_theme()

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
                font-family: 'Segoe UI';
            }
            
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }
            
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: none;
                border-radius: 25px;
                padding: 10px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #4d4d4d;
                transform: scale(1.05);
            }
            
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
            
            QSlider::groove:horizontal {
                border: none;
                height: 6px;
                background: #3d3d3d;
                border-radius: 3px;
            }
            
            QSlider::handle:horizontal {
                background: #4ecdc4;
                border: none;
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            
            QSlider::sub-page:horizontal {
                background: #4ecdc4;
                border-radius: 3px;
            }
            
            QListWidget {
                background-color: #2d2d2d;
                border-radius: 10px;
                border: none;
                padding: 5px;
            }
            
            QListWidget::item {
                padding: 8px;
                border-radius: 5px;
                margin: 2px;
            }
            
            QListWidget::item:selected {
                background-color: #4ecdc4;
                color: #000000;
            }
            
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
            
            QComboBox {
                background-color: #3d3d3d;
                border-radius: 5px;
                padding: 5px;
                color: #ffffff;
            }
            
            QComboBox::drop-down {
                border: none;
            }
            
            QComboBox::down-arrow {
                border: none;
            }
            
            QCheckBox {
                spacing: 5px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                background-color: #3d3d3d;
            }
            
            QCheckBox::indicator:checked {
                background-color: #4ecdc4;
            }
        """)

    def apply_light_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                color: #333333;
                font-family: 'Segoe UI';
            }
            
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
                border: 1px solid #e0e0e0;
            }
            
            QPushButton {
                background-color: #e3f2fd;
                color: #1976d2;
                border: 2px solid #1976d2;
                border-radius: 25px;
                padding: 10px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #1976d2;
                color: #ffffff;
            }
            
            QPushButton:pressed {
                background-color: #1565c0;
            }
            
            QSlider::groove:horizontal {
                border: none;
                height: 6px;
                background: #e0e0e0;
                border-radius: 3px;
            }
            
            QSlider::handle:horizontal {
                background: #1976d2;
                border: none;
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            
            QSlider::sub-page:horizontal {
                background: #1976d2;
                border-radius: 3px;
            }
            
            QListWidget {
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                padding: 5px;
            }
            
            QListWidget::item {
                padding: 8px;
                border-radius: 5px;
                margin: 2px;
            }
            
            QListWidget::item:selected {
                background-color: #1976d2;
                color: #ffffff;
            }
            
            QListWidget::item:hover {
                background-color: #e3f2fd;
            }
            
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 5px;
            }
        """)

    def apply_neon_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #0a0a0a;
                color: #00ffff;
                font-family: 'Segoe UI';
            }
            
            QFrame {
                background-color: #1a0d1a;
                border: 2px solid #ff00ff;
                border-radius: 15px;
                padding: 10px;
                margin: 5px;
            }
            
            QPushButton {
                background-color: #2d1b2d;
                color: #00ffff;
                border: 2px solid #00ffff;
                border-radius: 25px;
                padding: 10px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #00ffff;
                color: #0a0a0a;
                box-shadow: 0 0 20px #00ffff;
            }
            
            QPushButton:pressed {
                background-color: #ff00ff;
                border-color: #ff00ff;
            }
            
            QSlider::groove:horizontal {
                border: none;
                height: 8px;
                background: #2d1b2d;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff00ff, stop:1 #00ffff);
                border: 2px solid #ffffff;
                width: 20px;
                height: 20px;
                margin: -8px 0;
                border-radius: 12px;
            }
            
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff00ff, stop:1 #00ffff);
                border-radius: 4px;
            }
            
            QListWidget {
                background-color: #1a0d1a;
                border: 2px solid #ff00ff;
                border-radius: 10px;
                padding: 5px;
            }
            
            QListWidget::item {
                padding: 8px;
                border-radius: 5px;
                margin: 2px;
                color: #00ffff;
            }
            
            QListWidget::item:selected {
                background-color: #ff00ff;
                color: #000000;
            }
            
            QListWidget::item:hover {
                background-color: #2d1b2d;
                border: 1px solid #00ffff;
            }
            
            QComboBox {
                background-color: #2d1b2d;
                border: 2px solid #00ffff;
                border-radius: 5px;
                padding: 5px;
                color: #00ffff;
            }
            
            QLabel {
                color: #00ffff;
            }
        """)

    def change_theme(self, theme_text):
        if theme_text == "Dark Theme":
            self.apply_theme("dark")
        elif theme_text == "Light Theme":
            self.apply_theme("light")
        elif theme_text == "Neon Theme":
            self.apply_theme("neon")

    def toggle_fullscreen(self):
        if not self.is_fullscreen:
            self.video_widget.setParent(None)
            self.video_widget.showFullScreen()
            self.is_fullscreen = True
            self.fullscreen_btn.setText("🗗")
        else:
            self.video_widget.showNormal()
            self.video_frame.layout().insertWidget(0, self.video_widget)
            self.is_fullscreen = False
            self.fullscreen_btn.setText("⛶")

    def toggle_visualizer(self, checked):
        self.visualizer_frame.setVisible(checked)

    def change_volume(self, value):
        if not self.is_muted:
            self.audio_output.setVolume(value / 100.0)
        self.volume_label.setText(f"{value}%")
        
        if value == 0 or self.is_muted:
            if os.path.exists("icon_audio_off.png"):
                self.volume_icon_btn.setIcon(QIcon("icon_audio_off.png"))
        else:
            if os.path.exists("icon_audio_on.png"):
                self.volume_icon_btn.setIcon(QIcon("icon_audio_on.png"))

    def toggle_mute(self):
        if self.is_muted:
            self.volume_slider.setValue(self.previous_volume)
            self.audio_output.setVolume(self.previous_volume / 100.0)
            self.is_muted = False
            if os.path.exists("icon_audio_on.png"):
                self.volume_icon_btn.setIcon(QIcon("icon_audio_on.png"))
        else:
            self.previous_volume = self.volume_slider.value()
            self.audio_output.setVolume(0.0)
            self.is_muted = True
            if os.path.exists("icon_audio_off.png"):
                self.volume_icon_btn.setIcon(QIcon("icon_audio_off.png"))

    def toggle_repeat(self):
        self.repeat_mode = (self.repeat_mode + 1) % 3
        if self.repeat_mode == 0:
            self.repeat_btn.setStyleSheet("")
            if os.path.exists("icon_repeat.png"):
                self.repeat_btn.setIcon(QIcon("icon_repeat.png"))
        elif self.repeat_mode == 1:
            self.repeat_btn.setStyleSheet("background-color: #4ecdc4; color: #000000;")
            if os.path.exists("icon_repeat.png"):
                self.repeat_btn.setIcon(QIcon("icon_repeat.png"))
        elif self.repeat_mode == 2:
            self.repeat_btn.setStyleSheet("background-color: #ff6b6b; color: #000000;")
            if os.path.exists("repeat_one.png"):
                self.repeat_btn.setIcon(QIcon("repeat_one.png"))
            else:
                self.repeat_btn.setText("1")

    def toggle_shuffle(self):
        self.shuffle_enabled = not self.shuffle_enabled
        if self.shuffle_enabled:
            self.shuffled_indices = list(range(len(self.playlist)))
            random.shuffle(self.shuffled_indices)
            self.shuffle_btn.setStyleSheet(self.shuffle_btn.styleSheet() + "background-color: #4ecdc4; color: #000000;")
        else:
            self.shuffled_indices = []
            self.shuffle_btn.setStyleSheet("")

    def get_random_track(self):
        if len(self.playlist) <= 1:
            return self.current_index
            
        available_indices = list(range(len(self.playlist)))
        if self.current_index in available_indices:
            available_indices.remove(self.current_index)
        return random.choice(available_indices)

    def handle_media_finished(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self.repeat_mode == 2:
                self.player.setPosition(0)
                self.player.play()
            elif self.repeat_mode == 1:
                if self.shuffle_enabled:
                    self.play_media(self.get_random_track())
                else:
                    self.next_media()
            elif self.shuffle_enabled:
                self.play_media(self.get_random_track())

    def on_playback_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            if os.path.exists("icon_stop.png"):
                self.play_btn.setIcon(QIcon("icon_stop.png"))
            if self.is_audio_file():
                self.visualizer.start_visualization()
        else:
            if os.path.exists("icon_play.png"):
                self.play_btn.setIcon(QIcon("icon_play.png"))
            self.visualizer.stop_visualization()

    def is_audio_file(self):
        if self.current_index >= 0 and self.current_index < len(self.playlist):
            file_path = self.playlist[self.current_index]
            return file_path.lower().endswith(('.mp3', '.wav', '.flac', '.aac', '.ogg'))
        return False

    def open_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Media File", 
            "", 
            "Media Files (*.mp3 *.mp4 *.wav *.avi *.mkv *.flac *.aac *.ogg *.mov *.wmv)"
        )
        if file:
            self.add_to_playlist(file)
            self.play_media(len(self.playlist) - 1)

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder:
            extensions = ('.mp3', '.mp4', '.wav', '.avi', '.mkv', '.flac', '.aac', '.ogg', '.mov', '.wmv')
            files = [os.path.join(folder, f) for f in os.listdir(folder)
                     if f.lower().endswith(extensions)]
            for f in sorted(files):
                self.add_to_playlist(f)

    def clear_playlist(self):
        self.playlist.clear()
        self.track_list.clear()
        self.current_index = -1
        self.player.stop()
        self.current_track_label.setText("🎶 No media loaded")
        self.artist_label.setText("Playlist cleared")

    def add_to_playlist(self, file_path):
        if file_path not in self.playlist:
            self.playlist.append(file_path)
            filename = os.path.basename(file_path)
            self.track_list.addItem(f"{len(self.playlist)}. {filename}")

    def track_selected(self, item):
        index = self.track_list.row(item)
        self.play_media(index)

    def play_media(self, index):
        if index < 0 or index >= len(self.playlist):
            return
            
        self.current_index = index
        file_path = self.playlist[index]
        filename = os.path.basename(file_path)
        
        self.player.stop()
        
        self.player.setSource(QUrl.fromLocalFile(file_path))
        
        self.player.setAudioOutput(self.audio_output)
        if not self.is_muted:
            self.audio_output.setVolume(self.volume_slider.value() / 100.0)
        
        self.player.play()
        
        self.current_track_label.setText(f"🎵 {filename}")
        self.artist_label.setText(f"Track {index + 1} of {len(self.playlist)}")
        
        self.track_list.setCurrentRow(index)
        
        if self.is_audio_file():
            self.video_frame.hide()
            if self.visualizer_check.isChecked():
                self.visualizer_frame.show()
        else:
            self.visualizer_frame.hide()
            self.video_frame.show()
        
        self.timer.start()

    def on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.InvalidMedia:
            self.artist_label.setText("Invalid media file")
        elif status == QMediaPlayer.MediaStatus.LoadedMedia:
            self.artist_label.setText("Media loaded successfully")
        elif status == QMediaPlayer.MediaStatus.LoadingMedia:
            self.artist_label.setText("Loading media...")

    def on_error_occurred(self, error, error_string):
        print(f"Media player error: {error} - {error_string}")
        self.artist_label.setText(f"Error: {error_string}")

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        elif self.playlist:
            if self.current_index == -1:
                self.play_media(0)
            else:
                self.player.play()

    def next_media(self):
        if not self.playlist:
            return
            
        if self.shuffle_enabled:
            try:
                current_shuffle_index = self.shuffled_indices.index(self.current_index)
                if current_shuffle_index < len(self.shuffled_indices) - 1:
                    next_index = self.shuffled_indices[current_shuffle_index + 1]
                else:
                    if self.repeat_mode == 1:
                        random.shuffle(self.shuffled_indices)
                        next_index = self.shuffled_indices[0]
                    else:
                        return
            except ValueError:
                self.toggle_shuffle()
                self.toggle_shuffle()
                if self.shuffled_indices:
                    next_index = self.shuffled_indices[0]
                else:
                    return
        else:
            if self.current_index == len(self.playlist) - 1:
                if self.repeat_mode == 0:
                    return
                elif self.repeat_mode == 1:
                    next_index = 0
                else:
                    next_index = self.current_index
            else:
                next_index = self.current_index + 1
                
        self.play_media(next_index)

    def prev_media(self):
        if not self.playlist:
            return
            
        if self.shuffle_enabled:
            try:
                current_shuffle_index = self.shuffled_indices.index(self.current_index)
                if current_shuffle_index > 0:
                    prev_index = self.shuffled_indices[current_shuffle_index - 1]
                else:
                    if self.repeat_mode == 1:
                        prev_index = self.shuffled_indices[-1]
                    else:
                        return
            except ValueError:
                self.toggle_shuffle()
                self.toggle_shuffle()
                if self.shuffled_indices:
                    prev_index = self.shuffled_indices[-1]
                else:
                    return
        else:
            if self.current_index == 0:
                if self.repeat_mode == 0:
                    return
                elif self.repeat_mode == 1:
                    prev_index = len(self.playlist) - 1
                else:
                    prev_index = self.current_index
            else:
                prev_index = self.current_index - 1
                
        self.play_media(prev_index)

    def set_duration(self, duration):
        self.time_slider.setRange(0, duration)
        self.total_time_label.setText(self.ms_to_time(duration))

    def update_time_slider(self):
        if not self.time_slider.isSliderDown():
            self.time_slider.setValue(self.player.position())

    def update_time_display(self, position):
        self.current_time_label.setText(self.ms_to_time(position))
        if not self.time_slider.isSliderDown():
            self.time_slider.setValue(position)

    def seek_position(self, pos):
        self.player.setPosition(pos)

    def ms_to_time(self, ms):
        seconds = ms // 1000
        h, remainder = divmod(seconds, 3600)
        m, s = divmod(remainder, 60)
        if h > 0:
            return f"{int(h):02}:{int(m):02}:{int(s):02}"
        return f"{int(m):02}:{int(s):02}"

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.toggle_play()
            event.accept()
        elif event.key() == Qt.Key.Key_Right:
            self.next_media()
            event.accept()
        elif event.key() == Qt.Key.Key_Left:
            self.prev_media()
            event.accept()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.toggle_fullscreen()
            event.accept()
        else:
            super().keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setApplicationName("Neon Media Player Pro")
    app.setApplicationVersion("2.0")
    
    player = MediaPlayer()
    player.show()
    
    sys.exit(app.exec())