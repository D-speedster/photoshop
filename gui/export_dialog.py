from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox, QSlider, QGroupBox, QFileDialog)
from PyQt5.QtCore import Qt
import cv2


class ExportDialog(QDialog):
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.image = image
        self.setWindowTitle("Export Settings")
        self.setGeometry(300, 300, 400, 300)
        self.output_path = None
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        fmt_grp = QGroupBox("Format")
        fmt_lay = QVBoxLayout()
        self.fmt_cb = QComboBox()
        self.fmt_cb.addItems(["PNG (Lossless)", "JPEG (Compressed)", "BMP (Uncompressed)"])
        fmt_lay.addWidget(self.fmt_cb)
        fmt_grp.setLayout(fmt_lay)
        layout.addWidget(fmt_grp)
        
        qual_grp = QGroupBox("Quality (JPEG)")
        qual_lay = QVBoxLayout()
        self.qual_label = QLabel("Quality: 95%")
        qual_lay.addWidget(self.qual_label)
        self.qual_slider = QSlider(Qt.Horizontal)
        self.qual_slider.setRange(1, 100)
        self.qual_slider.setValue(95)
        self.qual_slider.valueChanged.connect(lambda v: self.qual_label.setText(f"Quality: {v}%"))
        qual_lay.addWidget(self.qual_slider)
        qual_grp.setLayout(qual_lay)
        layout.addWidget(qual_grp)
        
        size_grp = QGroupBox("Resize (Optional)")
        size_lay = QVBoxLayout()
        self.size_cb = QComboBox()
        h, w = self.image.shape[:2]
        self.size_cb.addItems([
            f"Original ({w}x{h})",
            f"75% ({int(w*0.75)}x{int(h*0.75)})",
            f"50% ({int(w*0.5)}x{int(h*0.5)})",
            f"25% ({int(w*0.25)}x{int(h*0.25)})"
        ])
        size_lay.addWidget(self.size_cb)
        size_grp.setLayout(size_lay)
        layout.addWidget(size_grp)
        
        btn_lay = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._export)
        btn_lay.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_lay.addWidget(cancel_btn)
        layout.addLayout(btn_lay)
        
    def _export(self):
        fmt_idx = self.fmt_cb.currentIndex()
        if fmt_idx == 0:
            filt = "PNG Files (*.png)"
            ext = ".png"
        elif fmt_idx == 1:
            filt = "JPEG Files (*.jpg *.jpeg)"
            ext = ".jpg"
        else:
            filt = "BMP Files (*.bmp)"
            ext = ".bmp"
            
        path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", filt)
        
        if path:
            if not any(path.endswith(e) for e in ['.png', '.jpg', '.jpeg', '.bmp']):
                path += ext
                
            size_idx = self.size_cb.currentIndex()
            if size_idx == 0:
                out = self.image
            else:
                scale = [1.0, 0.75, 0.5, 0.25][size_idx]
                h, w = self.image.shape[:2]
                out = cv2.resize(self.image, (int(w * scale), int(h * scale)))
                
            if fmt_idx == 1:
                cv2.imwrite(path, out, [cv2.IMWRITE_JPEG_QUALITY, self.qual_slider.value()])
            else:
                cv2.imwrite(path, out)
                
            self.output_path = path
            self.accept()
