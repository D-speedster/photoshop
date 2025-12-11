from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSlider, QGroupBox, QFileDialog, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import cv2


class ImageBlendDialog(QDialog):
    def __init__(self, image, processor, parent=None):
        super().__init__(parent)
        self.image1 = image
        self.image2 = None
        self.processor = processor
        self.result = None
        self.setWindowTitle("ادغام تصاویر")
        self.setGeometry(200, 200, 900, 700)
        self.setLayoutDirection(Qt.RightToLeft)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # انتخاب تصویر دوم
        img_grp = QGroupBox("تصویر دوم")
        img_lay = QHBoxLayout()
        
        self.img2_label = QLabel("تصویری انتخاب نشده")
        img_lay.addWidget(self.img2_label)
        
        select_btn = QPushButton("📂 انتخاب تصویر")
        select_btn.clicked.connect(self._select_image)
        img_lay.addWidget(select_btn)
        
        img_grp.setLayout(img_lay)
        layout.addWidget(img_grp)
        
        # نوع عملیات
        op_grp = QGroupBox("نوع عملیات")
        op_lay = QVBoxLayout()
        
        self.op_combo = QComboBox()
        self.op_combo.addItems([
            "ترکیب وزن‌دار (Blend)",
            "جمع تصاویر (Add)",
            "عملگر AND",
            "عملگر OR", 
            "عملگر XOR"
        ])
        self.op_combo.currentIndexChanged.connect(self._on_op_change)
        op_lay.addWidget(self.op_combo)
        
        # اسلایدر وزن
        weight_lay = QHBoxLayout()
        weight_lay.addWidget(QLabel("وزن تصویر اول:"))
        self.weight_label = QLabel("50%")
        weight_lay.addWidget(self.weight_label)
        op_lay.addLayout(weight_lay)
        
        self.weight_slider = QSlider(Qt.Horizontal)
        self.weight_slider.setRange(0, 100)
        self.weight_slider.setValue(50)
        self.weight_slider.valueChanged.connect(self._on_weight_change)
        op_lay.addWidget(self.weight_slider)
        
        op_grp.setLayout(op_lay)
        layout.addWidget(op_grp)
        
        # دکمه اعمال
        apply_btn = QPushButton("🔄 اعمال عملیات")
        apply_btn.clicked.connect(self._apply_operation)
        layout.addWidget(apply_btn)
        
        # پیش‌نمایش
        layout.addWidget(QLabel("پیش‌نمایش:"))
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setStyleSheet("background-color: #1e1e1e; border: 2px solid #444;")
        self.preview.setMinimumHeight(350)
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
        
        self._show_image(self.image1)
        
    def _select_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "انتخاب تصویر", "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self.image2 = cv2.imread(path)
            if self.image2 is not None:
                self.img2_label.setText(path.split('/')[-1])
                self._apply_operation()
                
    def _on_op_change(self, idx):
        self.weight_slider.setEnabled(idx == 0)
        if self.image2 is not None:
            self._apply_operation()
            
    def _on_weight_change(self, val):
        self.weight_label.setText(f"{val}%")
        if self.image2 is not None and self.op_combo.currentIndex() == 0:
            self._apply_operation()
            
    def _apply_operation(self):
        if self.image2 is None:
            return
            
        op = self.op_combo.currentIndex()
        
        if op == 0:  # Blend
            alpha = self.weight_slider.value() / 100.0
            self.result = self.processor.blend_images(self.image1, self.image2, alpha)
        elif op == 1:  # Add
            self.result = self.processor.add_images(self.image1, self.image2)
        elif op == 2:  # AND
            self.result = self.processor.bitwise_and(self.image1, self.image2)
        elif op == 3:  # OR
            self.result = self.processor.bitwise_or(self.image1, self.image2)
        elif op == 4:  # XOR
            self.result = self.processor.bitwise_xor(self.image1, self.image2)
            
        if self.result is not None:
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
