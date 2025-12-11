from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QCheckBox, QGroupBox, QSpinBox, QFileDialog,
                             QMessageBox, QSlider)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from camera.webcam import Webcam
import cv2
import os


class CameraWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.webcam = Webcam()
        self.timer = QTimer()
        self.setWindowTitle("دوربین")
        self.setGeometry(200, 200, 1000, 750)
        self.setLayoutDirection(Qt.RightToLeft)
        
        self.face_detect = False
        self.detect_eyes = False
        self.detect_smile = False
        self.blur_mode = False
        self.pixel_mode = False
        self.emoji_mode = False
        self.grayscale_mode = False
        self.pixel_size = 20
        self.frame = None
        self.processed = None
        
        self.recording = False
        self.video_writer = None
        self.paused = False
        self.delay_ms = 30
        
        self._setup_ui()
        
    def _setup_ui(self):
        main_lay = QHBoxLayout(self)
        
        left_lay = QVBoxLayout()
        
        self.display = QLabel()
        self.display.setAlignment(Qt.AlignCenter)
        self.display.setStyleSheet("background-color: black; border: 2px solid #444;")
        self.display.setMinimumSize(640, 480)
        left_lay.addWidget(self.display)
        
        self.face_info = QLabel("چهره‌ها: 0")
        left_lay.addWidget(self.face_info)
        
        # دکمه‌های اصلی
        btn_lay = QHBoxLayout()
        
        self.start_btn = QPushButton("▶️ شروع")
        self.start_btn.clicked.connect(self._start)
        btn_lay.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("⏸️ توقف")
        self.pause_btn.clicked.connect(self._toggle_pause)
        self.pause_btn.setEnabled(False)
        btn_lay.addWidget(self.pause_btn)
        
        self.capture_btn = QPushButton("📷 عکس")
        self.capture_btn.clicked.connect(self._capture)
        self.capture_btn.setEnabled(False)
        btn_lay.addWidget(self.capture_btn)
        
        self.stop_btn = QPushButton("⏹️ پایان")
        self.stop_btn.clicked.connect(self._stop)
        self.stop_btn.setEnabled(False)
        btn_lay.addWidget(self.stop_btn)
        
        left_lay.addLayout(btn_lay)
        
        # دکمه‌های ضبط ویدیو
        rec_lay = QHBoxLayout()
        
        self.rec_btn = QPushButton("🔴 شروع ضبط")
        self.rec_btn.clicked.connect(self._toggle_recording)
        self.rec_btn.setEnabled(False)
        rec_lay.addWidget(self.rec_btn)
        
        self.rec_status = QLabel("")
        rec_lay.addWidget(self.rec_status)
        
        left_lay.addLayout(rec_lay)
        
        main_lay.addLayout(left_lay, stretch=3)
        
        # پنل سمت راست
        right_lay = QVBoxLayout()
        
        # تنظیمات تاخیر
        delay_grp = QGroupBox("تنظیمات نمایش")
        delay_lay = QVBoxLayout()
        
        delay_info = QHBoxLayout()
        delay_info.addWidget(QLabel("تاخیر (ms):"))
        self.delay_label = QLabel("30")
        delay_info.addWidget(self.delay_label)
        delay_lay.addLayout(delay_info)
        
        self.delay_slider = QSlider(Qt.Horizontal)
        self.delay_slider.setRange(10, 200)
        self.delay_slider.setValue(30)
        self.delay_slider.valueChanged.connect(self._on_delay_change)
        delay_lay.addWidget(self.delay_slider)
        
        delay_grp.setLayout(delay_lay)
        right_lay.addWidget(delay_grp)
        
        # حالت خاکستری
        gray_grp = QGroupBox("حالت تصویر")
        gray_lay = QVBoxLayout()
        
        self.gray_chk = QCheckBox("🎞️ حالت خاکستری")
        self.gray_chk.stateChanged.connect(self._toggle_grayscale)
        gray_lay.addWidget(self.gray_chk)
        
        gray_grp.setLayout(gray_lay)
        right_lay.addWidget(gray_grp)
        
        # تشخیص چهره
        face_grp = QGroupBox("تشخیص چهره")
        face_lay = QVBoxLayout()
        
        self.face_chk = QCheckBox("فعال کردن تشخیص")
        self.face_chk.stateChanged.connect(self._toggle_face)
        face_lay.addWidget(self.face_chk)
        
        self.eyes_chk = QCheckBox("تشخیص چشم‌ها")
        self.eyes_chk.stateChanged.connect(self._update_settings)
        face_lay.addWidget(self.eyes_chk)
        
        self.smile_chk = QCheckBox("تشخیص لبخند")
        self.smile_chk.stateChanged.connect(self._update_settings)
        face_lay.addWidget(self.smile_chk)
        
        face_grp.setLayout(face_lay)
        right_lay.addWidget(face_grp)
        
        # افکت‌ها
        fx_grp = QGroupBox("افکت‌ها")
        fx_lay = QVBoxLayout()
        
        self.blur_chk = QCheckBox("محو کردن چهره")
        self.blur_chk.stateChanged.connect(self._toggle_blur)
        fx_lay.addWidget(self.blur_chk)
        
        self.pixel_chk = QCheckBox("پیکسلی کردن چهره")
        self.pixel_chk.stateChanged.connect(self._toggle_pixel)
        fx_lay.addWidget(self.pixel_chk)
        
        px_lay = QHBoxLayout()
        px_lay.addWidget(QLabel("اندازه پیکسل:"))
        self.px_spin = QSpinBox()
        self.px_spin.setRange(5, 50)
        self.px_spin.setValue(20)
        self.px_spin.valueChanged.connect(lambda v: setattr(self, 'pixel_size', v))
        px_lay.addWidget(self.px_spin)
        fx_lay.addLayout(px_lay)
        
        self.emoji_chk = QCheckBox("اضافه کردن عینک")
        self.emoji_chk.stateChanged.connect(self._toggle_emoji)
        fx_lay.addWidget(self.emoji_chk)
        
        fx_grp.setLayout(fx_lay)
        right_lay.addWidget(fx_grp)
        
        # راهنما
        help_label = QLabel("💡 برای خروج کلید Esc را بزنید")
        help_label.setStyleSheet("color: #888; font-size: 11px;")
        right_lay.addWidget(help_label)
        
        right_lay.addStretch()
        main_lay.addLayout(right_lay, stretch=1)
        
        self.timer.timeout.connect(self._update_frame)
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self._stop()
            self.close()
        elif event.key() == Qt.Key_Space:
            self._toggle_pause()
        
    def _on_delay_change(self, val):
        self.delay_ms = val
        self.delay_label.setText(str(val))
        if self.timer.isActive():
            self.timer.setInterval(val)
        
    def _start(self):
        if self.webcam.start():
            self.timer.start(self.delay_ms)
            self.start_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.capture_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            self.rec_btn.setEnabled(True)
        else:
            self.display.setText(f"خطای دوربین: {self.webcam.get_error()}")
            
    def _stop(self):
        if self.recording:
            self._stop_recording()
        self.timer.stop()
        self.webcam.stop()
        self.display.clear()
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.capture_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.rec_btn.setEnabled(False)
        self.paused = False
        self.pause_btn.setText("⏸️ توقف")
        
    def _toggle_pause(self):
        if not self.timer.isActive() and not self.paused:
            return
        self.paused = not self.paused
        if self.paused:
            self.timer.stop()
            self.pause_btn.setText("▶️ ادامه")
        else:
            self.timer.start(self.delay_ms)
            self.pause_btn.setText("⏸️ توقف")
            
    def _toggle_recording(self):
        if self.recording:
            self._stop_recording()
        else:
            self._start_recording()
            
    def _start_recording(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "ذخیره ویدیو", "", "Video Files (*.avi)"
        )
        if not path:
            return
        if not path.endswith('.avi'):
            path += '.avi'
            
        if self.frame is not None:
            h, w = self.frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            fps = 1000 / self.delay_ms
            self.video_writer = cv2.VideoWriter(path, fourcc, fps, (w, h), not self.grayscale_mode)
            self.recording = True
            self.rec_btn.setText("⏹️ پایان ضبط")
            self.rec_status.setText("🔴 در حال ضبط...")
            self.rec_status.setStyleSheet("color: red; font-weight: bold;")
            
    def _stop_recording(self):
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
        self.recording = False
        self.rec_btn.setText("🔴 شروع ضبط")
        self.rec_status.setText("✅ ذخیره شد")
        self.rec_status.setStyleSheet("color: green;")
        
    def _update_frame(self):
        frame = self.webcam.get_frame()
        if frame is None:
            err = self.webcam.get_error()
            if err:
                self.display.setText(f"خطا: {err}")
            return
            
        self.frame = frame.copy()
        processed = frame.copy()
        
        # اعمال حالت خاکستری
        if self.grayscale_mode:
            processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
            processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
        
        detector = self.main.processor.face_detection
        
        if self.blur_mode:
            processed = detector.blur_faces(processed)
            count = detector.count_faces(frame)
            self.face_info.setText(f"محو شده: {count}")
        elif self.pixel_mode:
            processed = detector.pixelate_faces(processed, self.pixel_size)
            count = detector.count_faces(frame)
            self.face_info.setText(f"پیکسلی: {count}")
        elif self.emoji_mode:
            processed = detector.add_emoji_to_faces(processed, 'sunglasses')
            count = detector.count_faces(frame)
            self.face_info.setText(f"چهره‌ها: {count}")
        elif self.face_detect:
            processed, data = detector.detect_faces(processed, self.detect_eyes, self.detect_smile)
            info = f"چهره‌ها: {len(data)}"
            if self.detect_eyes:
                eyes = sum(len(f['eyes']) for f in data)
                info += f" | چشم: {eyes}"
            if self.detect_smile:
                smiles = sum(len(f['smiles']) for f in data)
                info += f" | لبخند: {smiles}"
            self.face_info.setText(info)
        else:
            self.face_info.setText("چهره‌ها: 0")
        
        # ذخیره در ویدیو
        if self.recording and self.video_writer is not None:
            if self.grayscale_mode:
                gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
                self.video_writer.write(gray)
            else:
                self.video_writer.write(processed)
        
        # نمایش
        rgb = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.tobytes(), w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        scaled = pixmap.scaled(self.display.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.display.setPixmap(scaled)
        self.processed = processed
        
    def _toggle_grayscale(self, state):
        self.grayscale_mode = state == Qt.Checked
            
    def _toggle_face(self, state):
        self.face_detect = state == Qt.Checked
        if self.face_detect:
            self.blur_chk.setChecked(False)
            self.pixel_chk.setChecked(False)
            self.emoji_chk.setChecked(False)
    
    def _update_settings(self):
        self.detect_eyes = self.eyes_chk.isChecked()
        self.detect_smile = self.smile_chk.isChecked()
    
    def _toggle_blur(self, state):
        self.blur_mode = state == Qt.Checked
        if self.blur_mode:
            self.face_chk.setChecked(False)
            self.pixel_chk.setChecked(False)
            self.emoji_chk.setChecked(False)
    
    def _toggle_pixel(self, state):
        self.pixel_mode = state == Qt.Checked
        if self.pixel_mode:
            self.face_chk.setChecked(False)
            self.blur_chk.setChecked(False)
            self.emoji_chk.setChecked(False)
    
    def _toggle_emoji(self, state):
        self.emoji_mode = state == Qt.Checked
        if self.emoji_mode:
            self.face_chk.setChecked(False)
            self.blur_chk.setChecked(False)
            self.pixel_chk.setChecked(False)
    
    def _capture(self):
        img = self.processed if self.processed is not None else self.frame
        if img is not None:
            self.main.set_camera_image(img.copy())
            self._stop()
            self.close()
            
    def closeEvent(self, event):
        self._stop()
        event.accept()
