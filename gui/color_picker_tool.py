from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QApplication, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal


class ColorPickerTool(QWidget):
    color_picked = pyqtSignal(tuple)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.picking = False
        self.color = None
        self.setMaximumWidth(170)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        grp = QGroupBox("Color Picker")
        grp_lay = QVBoxLayout()
        
        self.pick_btn = QPushButton("Pick from Image")
        self.pick_btn.setCheckable(True)
        self.pick_btn.clicked.connect(self._toggle_mode)
        grp_lay.addWidget(self.pick_btn)
        
        color_lay = QHBoxLayout()
        color_lay.addWidget(QLabel("Color:"))
        self.color_box = QLabel()
        self.color_box.setMinimumSize(50, 30)
        self.color_box.setStyleSheet("background-color: #3c3c3c; border: 1px solid #5a5a5a;")
        color_lay.addWidget(self.color_box)
        grp_lay.addLayout(color_lay)
        
        self.rgb_label = QLabel("RGB: -")
        grp_lay.addWidget(self.rgb_label)
        
        self.hex_label = QLabel("HEX: -")
        grp_lay.addWidget(self.hex_label)
        
        copy_lay = QHBoxLayout()
        rgb_btn = QPushButton("Copy RGB")
        rgb_btn.clicked.connect(self._copy_rgb)
        copy_lay.addWidget(rgb_btn)
        
        hex_btn = QPushButton("Copy HEX")
        hex_btn.clicked.connect(self._copy_hex)
        copy_lay.addWidget(hex_btn)
        grp_lay.addLayout(copy_lay)
        
        use_btn = QPushButton("Use for Drawing")
        use_btn.clicked.connect(self._use_color)
        grp_lay.addWidget(use_btn)
        
        grp.setLayout(grp_lay)
        layout.addWidget(grp)
        layout.addStretch()
        
    def _toggle_mode(self, checked):
        self.picking = checked
        if checked:
            self.parent_window.image_label.setCursor(Qt.CrossCursor)
            self.parent_window.image_label.color_picker = self
            self.parent_window.image_label.active_mode = 'colorpicker'
        else:
            self.parent_window.image_label.setCursor(Qt.ArrowCursor)
            self.parent_window.image_label.color_picker = None
            self.parent_window.image_label.active_mode = None
            
    def handle_pick(self, pos):
        if self.parent_window.current_image is None:
            return
            
        label = self.parent_window.image_label
        img = self.parent_window.current_image
        img_h, img_w = img.shape[:2]
        
        scale_w = img_w / label.size().width()
        scale_h = img_h / label.size().height()
        scale = max(scale_w, scale_h)
        
        x = int(pos.x() * scale)
        y = int(pos.y() * scale)
        
        if 0 <= x < img_w and 0 <= y < img_h:
            b, g, r = img[y, x]
            self.color = (int(b), int(g), int(r))
            self._update_display(r, g, b)
            self.pick_btn.setChecked(False)
            self._toggle_mode(False)
            self.color_picked.emit(self.color)
            
    def _update_display(self, r, g, b):
        self.color_box.setStyleSheet(f"background-color: rgb({r},{g},{b}); border: 1px solid #5a5a5a;")
        self.rgb_label.setText(f"RGB: ({r}, {g}, {b})")
        self.hex_label.setText(f"HEX: #{r:02X}{g:02X}{b:02X}")
        
    def _copy_rgb(self):
        if self.color:
            b, g, r = self.color
            QApplication.clipboard().setText(f"({r}, {g}, {b})")
            
    def _copy_hex(self):
        if self.color:
            b, g, r = self.color
            QApplication.clipboard().setText(f"#{r:02X}{g:02X}{b:02X}")
            
    def _use_color(self):
        if self.color and hasattr(self.parent_window.image_label, 'draw_color'):
            self.parent_window.image_label.draw_color = self.color
            QMessageBox.information(self, "Done", "Color set for drawing tools")
