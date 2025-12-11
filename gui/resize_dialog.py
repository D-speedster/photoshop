from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QSpinBox, QCheckBox, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import cv2


class ResizeDialog(QDialog):
    MAX_DIMENSION = 8000
    
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.image = image
        self.setWindowTitle("Resize Image")
        self.setGeometry(200, 200, 600, 500)
        
        self.orig_w = image.shape[1]
        self.orig_h = image.shape[0]
        self.aspect = self.orig_w / self.orig_h if self.orig_h > 0 else 1
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        info = QLabel(f"Current size: {self.orig_w} x {self.orig_h}")
        layout.addWidget(info)
        
        size_grp = QGroupBox("New Size")
        size_lay = QVBoxLayout()
        
        w_lay = QHBoxLayout()
        w_lay.addWidget(QLabel("Width:"))
        self.w_spin = QSpinBox()
        self.w_spin.setRange(1, self.MAX_DIMENSION)
        self.w_spin.setValue(self.orig_w)
        self.w_spin.valueChanged.connect(self._on_width_change)
        w_lay.addWidget(self.w_spin)
        size_lay.addLayout(w_lay)
        
        h_lay = QHBoxLayout()
        h_lay.addWidget(QLabel("Height:"))
        self.h_spin = QSpinBox()
        self.h_spin.setRange(1, self.MAX_DIMENSION)
        self.h_spin.setValue(self.orig_h)
        self.h_spin.valueChanged.connect(self._on_height_change)
        h_lay.addWidget(self.h_spin)
        size_lay.addLayout(h_lay)
        
        self.keep_ratio = QCheckBox("Keep aspect ratio")
        self.keep_ratio.setChecked(True)
        size_lay.addWidget(self.keep_ratio)
        
        size_grp.setLayout(size_lay)
        layout.addWidget(size_grp)
        
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumSize(400, 300)
        layout.addWidget(self.preview)
        
        self._update_preview()
        
        btn_lay = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        btn_lay.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_lay.addWidget(cancel_btn)
        layout.addLayout(btn_lay)
        
    def _on_width_change(self, val):
        if self.keep_ratio.isChecked():
            new_h = int(val / self.aspect) if self.aspect > 0 else val
            new_h = max(1, min(new_h, self.MAX_DIMENSION))
            self.h_spin.blockSignals(True)
            self.h_spin.setValue(new_h)
            self.h_spin.blockSignals(False)
        self._update_preview()
        
    def _on_height_change(self, val):
        if self.keep_ratio.isChecked():
            new_w = int(val * self.aspect)
            new_w = max(1, min(new_w, self.MAX_DIMENSION))
            self.w_spin.blockSignals(True)
            self.w_spin.setValue(new_w)
            self.w_spin.blockSignals(False)
        self._update_preview()
        
    def _update_preview(self):
        new_w = self.w_spin.value()
        new_h = self.h_spin.value()
        
        resized = cv2.resize(self.image, (new_w, new_h))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.tobytes(), w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        scaled = pixmap.scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview.setPixmap(scaled)
        
    def get_resized_image(self):
        new_w = self.w_spin.value()
        new_h = self.h_spin.value()
        return cv2.resize(self.image, (new_w, new_h))
