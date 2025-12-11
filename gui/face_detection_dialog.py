from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QCheckBox, QGroupBox, QRadioButton, 
                             QButtonGroup, QMessageBox, QSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import cv2


class FaceDetectionDialog(QDialog):
    def __init__(self, image, detector, parent=None):
        super().__init__(parent)
        self.original = image.copy()
        self.result = None
        self.detector = detector
        
        self.setWindowTitle("تشخیص چهره")
        self.setGeometry(200, 200, 800, 600)
        self.setLayoutDirection(Qt.RightToLeft)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        
        # پنل تنظیمات (سمت راست)
        settings_lay = QVBoxLayout()
        settings_lay.setSpacing(6)
        
        # حالت تشخیص
        mode_grp = QGroupBox("حالت")
        mode_lay = QVBoxLayout()
        mode_lay.setSpacing(2)
        self.mode_grp = QButtonGroup()
        
        modes = [("تشخیص چهره", 1), ("محو کردن", 2), ("پیکسلی", 3), ("ایموجی", 4)]
        for text, idx in modes:
            rb = QRadioButton(text)
            if idx == 1: rb.setChecked(True)
            self.mode_grp.addButton(rb, idx)
            mode_lay.addWidget(rb)
        mode_grp.setLayout(mode_lay)
        settings_lay.addWidget(mode_grp)
        
        # گزینه‌ها
        opt_grp = QGroupBox("گزینه‌ها")
        opt_lay = QVBoxLayout()
        opt_lay.setSpacing(2)
        
        self.eyes_chk = QCheckBox("تشخیص چشم")
        self.smile_chk = QCheckBox("تشخیص لبخند")
        opt_lay.addWidget(self.eyes_chk)
        opt_lay.addWidget(self.smile_chk)
        
        # تنظیمات دقت
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("حداقل اندازه:"))
        self.min_spin = QSpinBox()
        self.min_spin.setRange(20, 150)
        self.min_spin.setValue(50)
        h1.addWidget(self.min_spin)
        opt_lay.addLayout(h1)
        
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("دقت:"))
        self.acc_spin = QSpinBox()
        self.acc_spin.setRange(3, 10)
        self.acc_spin.setValue(6)
        h2.addWidget(self.acc_spin)
        opt_lay.addLayout(h2)
        
        h3 = QHBoxLayout()
        h3.addWidget(QLabel("پیکسل:"))
        self.px_spin = QSpinBox()
        self.px_spin.setRange(5, 40)
        self.px_spin.setValue(15)
        h3.addWidget(self.px_spin)
        opt_lay.addLayout(h3)
        
        opt_grp.setLayout(opt_lay)
        settings_lay.addWidget(opt_grp)
        
        # ایموجی
        emoji_grp = QGroupBox("ایموجی")
        emoji_lay = QVBoxLayout()
        self.emoji_grp = QButtonGroup()
        self.glass_rb = QRadioButton("عینک 🕶️")
        self.glass_rb.setChecked(True)
        self.mask_rb = QRadioButton("ماسک 😷")
        self.emoji_grp.addButton(self.glass_rb, 1)
        self.emoji_grp.addButton(self.mask_rb, 2)
        emoji_lay.addWidget(self.glass_rb)
        emoji_lay.addWidget(self.mask_rb)
        emoji_grp.setLayout(emoji_lay)
        settings_lay.addWidget(emoji_grp)
        
        # دکمه اعمال
        apply_btn = QPushButton("🔍 اعمال")
        apply_btn.clicked.connect(self._apply)
        settings_lay.addWidget(apply_btn)
        
        # اطلاعات
        self.info_lbl = QLabel("چهره: ۰")
        self.info_lbl.setStyleSheet("color: #0078d4; font-weight: bold;")
        settings_lay.addWidget(self.info_lbl)
        
        settings_lay.addStretch()
        
        # دکمه‌های پایین
        btn_lay = QHBoxLayout()
        ok_btn = QPushButton("✅ تایید")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("❌ انصراف")
        cancel_btn.clicked.connect(self.reject)
        btn_lay.addWidget(ok_btn)
        btn_lay.addWidget(cancel_btn)
        settings_lay.addLayout(btn_lay)
        
        layout.addLayout(settings_lay)
        
        # پیش‌نمایش (سمت چپ)
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumSize(500, 400)
        self.preview.setStyleSheet("background: #1e1e1e; border: 1px solid #404040; border-radius: 4px;")
        layout.addWidget(self.preview, stretch=1)
        
        self._show_image(self.original)
        
    def _apply(self):
        mode = self.mode_grp.checkedId()
        min_s, acc = self.min_spin.value(), self.acc_spin.value()
        
        try:
            if mode == 1:
                self.result, data = self.detector.detect_faces_advanced(
                    self.original, self.eyes_chk.isChecked(), 
                    self.smile_chk.isChecked(), min_s, acc)
                info = f"چهره: {len(data)}"
                if self.eyes_chk.isChecked():
                    info += f" | چشم: {sum(len(f['eyes']) for f in data)}"
                if self.smile_chk.isChecked():
                    info += f" | لبخند: {sum(len(f['smiles']) for f in data)}"
                self.info_lbl.setText(info)
            elif mode == 2:
                self.result = self.detector.blur_faces_advanced(self.original, min_s, acc)
                self.info_lbl.setText(f"محو: {self.detector.count_faces_advanced(self.original, min_s, acc)}")
            elif mode == 3:
                self.result = self.detector.pixelate_faces_advanced(
                    self.original, self.px_spin.value(), min_s, acc)
                self.info_lbl.setText(f"پیکسلی: {self.detector.count_faces_advanced(self.original, min_s, acc)}")
            elif mode == 4:
                etype = 'sunglasses' if self.emoji_grp.checkedId() == 1 else 'mask'
                self.result = self.detector.add_emoji_advanced(self.original, etype, min_s, acc)
                self.info_lbl.setText(f"ایموجی: {self.detector.count_faces_advanced(self.original, min_s, acc)}")
            
            if self.result is not None:
                self._show_image(self.result)
        except Exception as e:
            QMessageBox.critical(self, "خطا", str(e))
    
    def _show_image(self, img):
        if img is None: return
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, c = rgb.shape
        qimg = QImage(rgb.tobytes(), w, h, c * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg).scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview.setPixmap(pix)
    
    def get_processed_image(self):
        return self.result if self.result is not None else self.original
