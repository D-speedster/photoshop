from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSlider, QGroupBox, QSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import cv2


class RotateDialog(QDialog):
    def __init__(self, image, processor, parent=None):
        super().__init__(parent)
        self.image = image
        self.processor = processor
        self.result = None
        self.setWindowTitle("چرخش تصویر")
        self.setGeometry(200, 200, 800, 650)
        self.setLayoutDirection(Qt.RightToLeft)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # زاویه چرخش
        angle_grp = QGroupBox("زاویه چرخش")
        angle_lay = QVBoxLayout()
        
        # دکمه‌های سریع
        quick_lay = QHBoxLayout()
        for angle in [30, 45, 60, 90, 180, -90]:
            btn = QPushButton(f"{angle}°")
            btn.clicked.connect(lambda _, a=angle: self._set_angle(a))
            quick_lay.addWidget(btn)
        angle_lay.addLayout(quick_lay)
        
        # اسلایدر
        slider_lay = QHBoxLayout()
        slider_lay.addWidget(QLabel("زاویه:"))
        
        self.angle_spin = QSpinBox()
        self.angle_spin.setRange(-180, 180)
        self.angle_spin.setValue(0)
        self.angle_spin.valueChanged.connect(self._on_angle_change)
        slider_lay.addWidget(self.angle_spin)
        
        self.angle_label = QLabel("0°")
        slider_lay.addWidget(self.angle_label)
        angle_lay.addLayout(slider_lay)
        
        self.angle_slider = QSlider(Qt.Horizontal)
        self.angle_slider.setRange(-180, 180)
        self.angle_slider.setValue(0)
        self.angle_slider.valueChanged.connect(self._on_slider_change)
        angle_lay.addWidget(self.angle_slider)
        
        angle_grp.setLayout(angle_lay)
        layout.addWidget(angle_grp)
        
        # پیش‌نمایش
        layout.addWidget(QLabel("پیش‌نمایش:"))
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setStyleSheet("background-color: #1e1e1e; border: 2px solid #444;")
        self.preview.setMinimumHeight(400)
        layout.addWidget(self.preview)
        
        # دکمه‌ها
        btn_lay = QHBoxLayout()
        
        ok_btn = QPushButton("✅ تایید")
        ok_btn.clicked.connect(self.accept)
        btn_lay.addWidget(ok_btn)
        
        cancel_btn = QPushButton("❌ انصراف")
        cancel_btn.clicked.connect(self.reject)
        btn_lay.addWidget(cancel_btn)
        
        layout.addLayout(btn_lay)
        
        self._update_preview()
        
    def _set_angle(self, angle):
        self.angle_spin.setValue(angle)
        self.angle_slider.setValue(angle)
        
    def _on_slider_change(self, val):
        self.angle_spin.blockSignals(True)
        self.angle_spin.setValue(val)
        self.angle_spin.blockSignals(False)
        self.angle_label.setText(f"{val}°")
        self._update_preview()
        
    def _on_angle_change(self, val):
        self.angle_slider.blockSignals(True)
        self.angle_slider.setValue(val)
        self.angle_slider.blockSignals(False)
        self.angle_label.setText(f"{val}°")
        self._update_preview()
        
    def _update_preview(self):
        angle = self.angle_spin.value()
        if angle == 0:
            self.result = self.image.copy()
        elif angle in [90, -90, 180]:
            self.result = self.processor.rotate(self.image, angle)
        else:
            self.result = self.processor.rotate_free(self.image, angle)
        self._show_image(self.result)
        
    def _show_image(self, image):
        if image is None:
            return
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.tobytes(), w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        scaled = pixmap.scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview.setPixmap(scaled)
        
    def get_result(self):
        return self.result
