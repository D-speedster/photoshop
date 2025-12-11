from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSpinBox, QGroupBox, QComboBox, QColorDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import cv2
import numpy as np


class ShapeGeneratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result = None
        self.bg_color = (255, 255, 255)
        self.shape_color = (0, 0, 255)
        self.setWindowTitle("ساخت اشکال هندسی")
        self.setGeometry(200, 200, 700, 650)
        self.setLayoutDirection(Qt.RightToLeft)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # اندازه تصویر
        size_grp = QGroupBox("اندازه تصویر")
        size_lay = QHBoxLayout()
        
        size_lay.addWidget(QLabel("عرض:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 2000)
        self.width_spin.setValue(500)
        size_lay.addWidget(self.width_spin)
        
        size_lay.addWidget(QLabel("ارتفاع:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 2000)
        self.height_spin.setValue(500)
        size_lay.addWidget(self.height_spin)
        
        size_grp.setLayout(size_lay)
        layout.addWidget(size_grp)
        
        # نوع شکل
        shape_grp = QGroupBox("نوع شکل")
        shape_lay = QVBoxLayout()
        
        self.shape_combo = QComboBox()
        self.shape_combo.addItems([
            "مستطیل",
            "دایره",
            "بیضی",
            "مثلث",
            "پنج‌ضلعی",
            "شش‌ضلعی",
            "ستاره",
            "خطوط شبکه‌ای"
        ])
        self.shape_combo.currentIndexChanged.connect(self._update_preview)
        shape_lay.addWidget(self.shape_combo)
        
        shape_grp.setLayout(shape_lay)
        layout.addWidget(shape_grp)
        
        # رنگ‌ها
        color_grp = QGroupBox("رنگ‌ها")
        color_lay = QHBoxLayout()
        
        self.bg_btn = QPushButton("رنگ پس‌زمینه")
        self.bg_btn.clicked.connect(self._select_bg_color)
        self.bg_preview = QLabel()
        self.bg_preview.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        self.bg_preview.setMinimumSize(30, 25)
        color_lay.addWidget(self.bg_btn)
        color_lay.addWidget(self.bg_preview)
        
        self.shape_btn = QPushButton("رنگ شکل")
        self.shape_btn.clicked.connect(self._select_shape_color)
        self.shape_preview = QLabel()
        self.shape_preview.setStyleSheet("background-color: red; border: 1px solid #ccc;")
        self.shape_preview.setMinimumSize(30, 25)
        color_lay.addWidget(self.shape_btn)
        color_lay.addWidget(self.shape_preview)
        
        color_grp.setLayout(color_lay)
        layout.addWidget(color_grp)
        
        # ضخامت خط
        thick_grp = QGroupBox("ضخامت خط")
        thick_lay = QHBoxLayout()
        thick_lay.addWidget(QLabel("ضخامت:"))
        self.thick_spin = QSpinBox()
        self.thick_spin.setRange(1, 20)
        self.thick_spin.setValue(3)
        self.thick_spin.valueChanged.connect(self._update_preview)
        thick_lay.addWidget(self.thick_spin)
        thick_grp.setLayout(thick_lay)
        layout.addWidget(thick_grp)
        
        # دکمه ایجاد
        gen_btn = QPushButton("🎨 ایجاد شکل")
        gen_btn.clicked.connect(self._update_preview)
        layout.addWidget(gen_btn)
        
        # پیش‌نمایش
        layout.addWidget(QLabel("پیش‌نمایش:"))
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setStyleSheet("background-color: #1e1e1e; border: 2px solid #444;")
        self.preview.setMinimumHeight(300)
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
        
    def _select_bg_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.bg_color = (color.blue(), color.green(), color.red())
            self.bg_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
            self._update_preview()
            
    def _select_shape_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.shape_color = (color.blue(), color.green(), color.red())
            self.shape_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
            self._update_preview()
            
    def _update_preview(self):
        w = self.width_spin.value()
        h = self.height_spin.value()
        thick = self.thick_spin.value()
        shape_idx = self.shape_combo.currentIndex()
        
        img = np.full((h, w, 3), self.bg_color, dtype=np.uint8)
        cx, cy = w // 2, h // 2
        size = min(w, h) // 3
        
        if shape_idx == 0:  # مستطیل
            cv2.rectangle(img, (cx - size, cy - size//2), (cx + size, cy + size//2), self.shape_color, thick)
        elif shape_idx == 1:  # دایره
            cv2.circle(img, (cx, cy), size, self.shape_color, thick)
        elif shape_idx == 2:  # بیضی
            cv2.ellipse(img, (cx, cy), (size, size//2), 0, 0, 360, self.shape_color, thick)
        elif shape_idx == 3:  # مثلث
            pts = np.array([[cx, cy - size], [cx - size, cy + size], [cx + size, cy + size]], np.int32)
            cv2.polylines(img, [pts], True, self.shape_color, thick)
        elif shape_idx == 4:  # پنج‌ضلعی
            pts = self._polygon_points(cx, cy, size, 5)
            cv2.polylines(img, [pts], True, self.shape_color, thick)
        elif shape_idx == 5:  # شش‌ضلعی
            pts = self._polygon_points(cx, cy, size, 6)
            cv2.polylines(img, [pts], True, self.shape_color, thick)
        elif shape_idx == 6:  # ستاره
            pts = self._star_points(cx, cy, size, size//2, 5)
            cv2.polylines(img, [pts], True, self.shape_color, thick)
        elif shape_idx == 7:  # خطوط شبکه‌ای
            step = 50
            for x in range(0, w, step):
                cv2.line(img, (x, 0), (x, h), self.shape_color, 1)
            for y in range(0, h, step):
                cv2.line(img, (0, y), (w, y), self.shape_color, 1)
        
        self.result = img
        self._show_image(img)
        
    def _polygon_points(self, cx, cy, radius, sides):
        angles = np.linspace(0, 2 * np.pi, sides, endpoint=False) - np.pi / 2
        pts = []
        for a in angles:
            x = int(cx + radius * np.cos(a))
            y = int(cy + radius * np.sin(a))
            pts.append([x, y])
        return np.array(pts, np.int32)
    
    def _star_points(self, cx, cy, outer_r, inner_r, points):
        angles = np.linspace(0, 2 * np.pi, points * 2, endpoint=False) - np.pi / 2
        pts = []
        for i, a in enumerate(angles):
            r = outer_r if i % 2 == 0 else inner_r
            x = int(cx + r * np.cos(a))
            y = int(cy + r * np.sin(a))
            pts.append([x, y])
        return np.array(pts, np.int32)
        
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
