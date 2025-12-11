from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSlider, QGroupBox, QFileDialog, QComboBox,
                             QCheckBox, QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
import cv2


class VideoProcessorDialog(QDialog):
    def __init__(self, processor, parent=None):
        super().__init__(parent)
        self.processor = processor
        self.cap = None
        self.timer = QTimer()
        self.paused = False
        self.current_frame = None
        self.total_frames = 0
        self.current_pos = 0
        self.grayscale = False
        self.filter_name = None
        
        self.setWindowTitle("پردازش ویدیو")
        self.setGeometry(200, 200, 900, 700)
        self.setLayoutDirection(Qt.RightToLeft)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # انتخاب فایل
        file_grp = QGroupBox("فایل ویدیو")
        file_lay = QHBoxLayout()
        
        self.file_label = QLabel("فایلی انتخاب نشده")
        file_lay.addWidget(self.file_label)
        
        open_btn = QPushButton("📂 انتخاب ویدیو")
        open_btn.clicked.connect(self._open_video)
        file_lay.addWidget(open_btn)
        
        file_grp.setLayout(file_lay)
        layout.addWidget(file_grp)
        
        # نمایش ویدیو
        self.display = QLabel()
        self.display.setAlignment(Qt.AlignCenter)
        self.display.setStyleSheet("background-color: #1e1e1e; border: 2px solid #444;")
        self.display.setMinimumHeight(400)
        layout.addWidget(self.display)
        
        # نوار پیشرفت
        self.progress = QSlider(Qt.Horizontal)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.sliderMoved.connect(self._seek)
        layout.addWidget(self.progress)
        
        # اطلاعات
        info_lay = QHBoxLayout()
        self.time_label = QLabel("00:00 / 00:00")
        info_lay.addWidget(self.time_label)
        info_lay.addStretch()
        self.fps_label = QLabel("FPS: -")
        info_lay.addWidget(self.fps_label)
        layout.addLayout(info_lay)
        
        # کنترل‌ها
        ctrl_lay = QHBoxLayout()
        
        self.play_btn = QPushButton("▶️ پخش")
        self.play_btn.clicked.connect(self._toggle_play)
        self.play_btn.setEnabled(False)
        ctrl_lay.addWidget(self.play_btn)
        
        self.stop_btn = QPushButton("⏹️ توقف")
        self.stop_btn.clicked.connect(self._stop)
        self.stop_btn.setEnabled(False)
        ctrl_lay.addWidget(self.stop_btn)
        
        self.capture_btn = QPushButton("📷 ذخیره فریم")
        self.capture_btn.clicked.connect(self._capture_frame)
        self.capture_btn.setEnabled(False)
        ctrl_lay.addWidget(self.capture_btn)
        
        layout.addLayout(ctrl_lay)
        
        # تنظیمات پردازش
        proc_grp = QGroupBox("پردازش")
        proc_lay = QVBoxLayout()
        
        self.gray_chk = QCheckBox("🎞️ تبدیل به خاکستری")
        self.gray_chk.stateChanged.connect(lambda s: setattr(self, 'grayscale', s == Qt.Checked))
        proc_lay.addWidget(self.gray_chk)
        
        filter_lay = QHBoxLayout()
        filter_lay.addWidget(QLabel("فیلتر:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "بدون فیلتر",
            "محو (Blur)",
            "شارپ",
            "تشخیص لبه",
            "خاکستری",
            "معکوس",
            "کارتونی"
        ])
        self.filter_combo.currentIndexChanged.connect(self._on_filter_change)
        filter_lay.addWidget(self.filter_combo)
        proc_lay.addLayout(filter_lay)
        
        proc_grp.setLayout(proc_lay)
        layout.addWidget(proc_grp)
        
        # دکمه بستن
        close_btn = QPushButton("❌ بستن")
        close_btn.clicked.connect(self._close)
        layout.addWidget(close_btn)
        
        self.timer.timeout.connect(self._read_frame)
        
    def _open_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "انتخاب ویدیو", "",
            "Video Files (*.mp4 *.avi *.mkv *.mov)"
        )
        if not path:
            return
            
        if self.cap is not None:
            self.cap.release()
            
        self.cap = cv2.VideoCapture(path)
        if not self.cap.isOpened():
            QMessageBox.warning(self, "خطا", "نمی‌توان ویدیو را باز کرد")
            return
            
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.fps_label.setText(f"FPS: {fps:.1f}")
        
        duration = self.total_frames / fps if fps > 0 else 0
        mins = int(duration // 60)
        secs = int(duration % 60)
        self.time_label.setText(f"00:00 / {mins:02d}:{secs:02d}")
        
        self.file_label.setText(path.split('/')[-1])
        self.progress.setRange(0, self.total_frames)
        
        self.play_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.capture_btn.setEnabled(True)
        
        self._read_frame()
        
    def _on_filter_change(self, idx):
        filters = [None, 'blur', 'sharpen', 'edge', 'grayscale', 'invert', 'cartoon']
        self.filter_name = filters[idx] if idx > 0 else None
        
    def _toggle_play(self):
        if self.cap is None:
            return
            
        if self.timer.isActive():
            self.timer.stop()
            self.play_btn.setText("▶️ پخش")
            self.paused = True
        else:
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            interval = int(1000 / fps) if fps > 0 else 33
            self.timer.start(interval)
            self.play_btn.setText("⏸️ توقف")
            self.paused = False
            
    def _stop(self):
        self.timer.stop()
        if self.cap is not None:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.current_pos = 0
        self.progress.setValue(0)
        self.play_btn.setText("▶️ پخش")
        self._read_frame()
        
    def _seek(self, pos):
        if self.cap is not None:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
            self._read_frame()
            
    def _read_frame(self):
        if self.cap is None:
            return
            
        ret, frame = self.cap.read()
        if not ret:
            self.timer.stop()
            self.play_btn.setText("▶️ پخش")
            return
            
        self.current_frame = frame.copy()
        self.current_pos = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        self.progress.setValue(self.current_pos)
        
        # آپدیت زمان
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        if fps > 0:
            current_time = self.current_pos / fps
            total_time = self.total_frames / fps
            cur_m, cur_s = int(current_time // 60), int(current_time % 60)
            tot_m, tot_s = int(total_time // 60), int(total_time % 60)
            self.time_label.setText(f"{cur_m:02d}:{cur_s:02d} / {tot_m:02d}:{tot_s:02d}")
        
        # پردازش
        processed = frame.copy()
        
        if self.grayscale:
            processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
            processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
            
        if self.filter_name:
            processed = self.processor.apply_filter(processed, self.filter_name)
        
        # نمایش
        rgb = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.tobytes(), w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        scaled = pixmap.scaled(self.display.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.display.setPixmap(scaled)
        
    def _capture_frame(self):
        if self.current_frame is None:
            return
            
        path, _ = QFileDialog.getSaveFileName(
            self, "ذخیره فریم", "", "Images (*.png *.jpg)"
        )
        if path:
            frame = self.current_frame.copy()
            if self.grayscale:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            if self.filter_name:
                frame = self.processor.apply_filter(frame, self.filter_name)
            cv2.imwrite(path, frame)
            QMessageBox.information(self, "موفق", "فریم ذخیره شد")
            
    def _close(self):
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
        self.accept()
        
    def closeEvent(self, event):
        self._close()
        event.accept()
