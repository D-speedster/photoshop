from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QSpinBox, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import cv2


class CropDialog(QDialog):
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.image = image
        self.setWindowTitle("Crop Image")
        self.setGeometry(200, 200, 800, 700)
        
        self.img_h, self.img_w = image.shape[:2]
        self.crop_x = 0
        self.crop_y = 0
        self.crop_w = self.img_w
        self.crop_h = self.img_h
        
        self._setup_ui()
        self._update_preview()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumSize(600, 400)
        layout.addWidget(self.preview)
        
        settings = QGroupBox("Crop Settings")
        s_layout = QHBoxLayout()
        
        s_layout.addWidget(QLabel("X:"))
        self.x_spin = QSpinBox()
        self.x_spin.setMaximum(self.img_w - 1)
        self.x_spin.valueChanged.connect(self._on_change)
        s_layout.addWidget(self.x_spin)
        
        s_layout.addWidget(QLabel("Y:"))
        self.y_spin = QSpinBox()
        self.y_spin.setMaximum(self.img_h - 1)
        self.y_spin.valueChanged.connect(self._on_change)
        s_layout.addWidget(self.y_spin)
        
        s_layout.addWidget(QLabel("Width:"))
        self.w_spin = QSpinBox()
        self.w_spin.setRange(1, self.img_w)
        self.w_spin.setValue(self.img_w)
        self.w_spin.valueChanged.connect(self._on_change)
        s_layout.addWidget(self.w_spin)
        
        s_layout.addWidget(QLabel("Height:"))
        self.h_spin = QSpinBox()
        self.h_spin.setRange(1, self.img_h)
        self.h_spin.setValue(self.img_h)
        self.h_spin.valueChanged.connect(self._on_change)
        s_layout.addWidget(self.h_spin)
        
        settings.setLayout(s_layout)
        layout.addWidget(settings)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
    def _on_change(self):
        self.crop_x = min(self.x_spin.value(), self.img_w - 1)
        self.crop_y = min(self.y_spin.value(), self.img_h - 1)
        self.crop_w = min(self.w_spin.value(), self.img_w - self.crop_x)
        self.crop_h = min(self.h_spin.value(), self.img_h - self.crop_y)
        self._update_preview()
        
    def _update_preview(self):
        preview_img = self.image.copy()
        x2 = min(self.crop_x + self.crop_w, self.img_w)
        y2 = min(self.crop_y + self.crop_h, self.img_h)
        cv2.rectangle(preview_img, (self.crop_x, self.crop_y), (x2, y2), (0, 255, 0), 2)
        
        rgb = cv2.cvtColor(preview_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.tobytes(), w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        scaled = pixmap.scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview.setPixmap(scaled)
        
    def get_cropped_image(self):
        x2 = min(self.crop_x + self.crop_w, self.img_w)
        y2 = min(self.crop_y + self.crop_h, self.img_h)
        if x2 > self.crop_x and y2 > self.crop_y:
            return self.image[self.crop_y:y2, self.crop_x:x2]
        return self.image
