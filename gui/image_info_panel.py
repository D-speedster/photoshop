from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox
import os


class ImageInfoPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(170)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        grp = QGroupBox("Image Info")
        grp_lay = QVBoxLayout()
        
        self.size_lbl = QLabel("Size: -")
        self.fmt_lbl = QLabel("Format: -")
        self.file_lbl = QLabel("File Size: -")
        self.depth_lbl = QLabel("Channels: -")
        self.zoom_lbl = QLabel("Zoom: 100%")
        
        for lbl in [self.size_lbl, self.fmt_lbl, self.file_lbl, self.depth_lbl, self.zoom_lbl]:
            grp_lay.addWidget(lbl)
            
        grp.setLayout(grp_lay)
        layout.addWidget(grp)
        layout.addStretch()
        
    def update_info(self, image, path=None):
        if image is None:
            self._clear()
            return
            
        h, w = image.shape[:2]
        ch = image.shape[2] if len(image.shape) > 2 else 1
        
        self.size_lbl.setText(f"Size: {w} x {h}")
        self.depth_lbl.setText(f"Channels: {ch}")
        
        if path and os.path.exists(path):
            size = os.path.getsize(path)
            kb = size / 1024
            if kb > 1024:
                self.file_lbl.setText(f"File Size: {kb/1024:.2f} MB")
            else:
                self.file_lbl.setText(f"File Size: {kb:.2f} KB")
            self.fmt_lbl.setText(f"Format: {os.path.splitext(path)[1].upper()}")
        else:
            self.file_lbl.setText("File Size: -")
            self.fmt_lbl.setText("Format: -")
            
    def update_zoom(self, level):
        self.zoom_lbl.setText(f"Zoom: {level}%")
        
    def _clear(self):
        self.size_lbl.setText("Size: -")
        self.fmt_lbl.setText("Format: -")
        self.file_lbl.setText("File Size: -")
        self.depth_lbl.setText("Channels: -")
        self.zoom_lbl.setText("Zoom: 100%")
