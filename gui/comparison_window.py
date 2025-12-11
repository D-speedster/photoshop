from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import cv2
import numpy as np


class ComparisonWindow(QWidget):
    def __init__(self, original, edited, parent=None):
        super().__init__(parent)
        self.original = original
        self.edited = edited
        self.setWindowTitle("Before / After")
        self.setGeometry(200, 200, 1000, 600)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.display = QLabel()
        self.display.setAlignment(Qt.AlignCenter)
        self.display.setMinimumSize(800, 500)
        layout.addWidget(self.display)
        
        slider_lay = QHBoxLayout()
        slider_lay.addWidget(QLabel("Before"))
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self._update_view)
        slider_lay.addWidget(self.slider)
        
        slider_lay.addWidget(QLabel("After"))
        layout.addLayout(slider_lay)
        
        btn_lay = QHBoxLayout()
        
        side_btn = QPushButton("Side by Side")
        side_btn.clicked.connect(self._show_side_by_side)
        btn_lay.addWidget(side_btn)
        
        split_btn = QPushButton("Split View")
        split_btn.clicked.connect(lambda: self.slider.setValue(50))
        btn_lay.addWidget(split_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_lay.addWidget(close_btn)
        
        layout.addLayout(btn_lay)
        self._update_view(50)
        
    def _update_view(self, value):
        orig_h, orig_w = self.original.shape[:2]
        edit_h, edit_w = self.edited.shape[:2]
        
        if orig_h != edit_h or orig_w != edit_w:
            edited = cv2.resize(self.edited, (orig_w, orig_h))
        else:
            edited = self.edited
            
        split_x = int(orig_w * value / 100)
        combined = np.zeros_like(self.original)
        combined[:, :split_x] = self.original[:, :split_x]
        combined[:, split_x:] = edited[:, split_x:]
        
        cv2.line(combined, (split_x, 0), (split_x, orig_h), (0, 255, 0), 2)
        self._show_image(combined)
        
    def _show_side_by_side(self):
        orig_h, orig_w = self.original.shape[:2]
        edit_h, edit_w = self.edited.shape[:2]
        
        if orig_h != edit_h:
            edited = cv2.resize(self.edited, (edit_w, orig_h))
        else:
            edited = self.edited
            
        combined = np.hstack([self.original, edited])
        self._show_image(combined)
        
    def _show_image(self, image):
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.tobytes(), w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        scaled = pixmap.scaled(self.display.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.display.setPixmap(scaled)
