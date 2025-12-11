from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSlider, QGroupBox, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import cv2
import numpy as np


class SplitViewDialog(QDialog):
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.image = image
        self.result = None
        self.setWindowTitle("نمایش همزمان رنگی و خاکستری")
        self.setGeometry(200, 200, 900, 700)
        self.setLayoutDirection(Qt.RightToLeft)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # نوع نمایش
        mode_grp = QGroupBox("نوع نمایش")
        mode_lay = QVBoxLayout()
        
        self.mode_group = QButtonGroup()
        
        self.split_rb = QRadioButton("تقسیم عمودی (رنگی | خاکستری)")
        self.split_rb.setChecked(True)
        self.mode_group.addButton(self.split_rb, 0)
        mode_lay.addWidget(self.split_rb)
        
        self.side_rb = QRadioButton("کنار هم (رنگی - خاکستری)")
        self.mode_group.addButton(self.side_rb, 1)
        mode_lay.addWidget(self.side_rb)
        
        self.top_rb = QRadioButton("بالا و پایین")
        self.mode_group.addButton(self.top_rb, 2)
        mode_lay.addWidget(self.top_rb)
        
        self.mode_group.buttonClicked.connect(self._update_preview)
        
        mode_grp.setLayout(mode_lay)
        layout.addWidget(mode_grp)
        
        # اسلایدر موقعیت تقسیم
        pos_grp = QGroupBox("موقعیت تقسیم")
        pos_lay = QVBoxLayout()
        
        pos_info = QHBoxLayout()
        pos_info.addWidget(QLabel("رنگی"))
        self.pos_label = QLabel("50%")
        pos_info.addWidget(self.pos_label)
        pos_info.addWidget(QLabel("خاکستری"))
        pos_lay.addLayout(pos_info)
        
        self.pos_slider = QSlider(Qt.Horizontal)
        self.pos_slider.setRange(10, 90)
        self.pos_slider.setValue(50)
        self.pos_slider.valueChanged.connect(self._on_pos_change)
        pos_lay.addWidget(self.pos_slider)
        
        pos_grp.setLayout(pos_lay)
        layout.addWidget(pos_grp)
        
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
        
    def _on_pos_change(self, val):
        self.pos_label.setText(f"{val}%")
        self._update_preview()
        
    def _update_preview(self):
        mode = self.mode_group.checkedId()
        pos = self.pos_slider.value()
        
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        h, w = self.image.shape[:2]
        
        if mode == 0:  # تقسیم عمودی
            split_x = int(w * pos / 100)
            self.result = self.image.copy()
            self.result[:, split_x:] = gray_bgr[:, split_x:]
            cv2.line(self.result, (split_x, 0), (split_x, h), (0, 255, 0), 2)
            self.pos_slider.setEnabled(True)
            
        elif mode == 1:  # کنار هم
            self.result = np.hstack([self.image, gray_bgr])
            self.pos_slider.setEnabled(False)
            
        elif mode == 2:  # بالا و پایین
            self.result = np.vstack([self.image, gray_bgr])
            self.pos_slider.setEnabled(False)
            
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
