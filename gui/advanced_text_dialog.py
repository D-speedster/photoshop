from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSpinBox, QComboBox, QGroupBox,
                             QColorDialog, QCheckBox, QTextEdit)
from PyQt5.QtCore import Qt
import cv2


class AdvancedTextDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Text Settings")
        self.setGeometry(300, 300, 500, 600)
        self.text_color = (255, 255, 255)
        self.bg_color = None
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        txt_grp = QGroupBox("Text")
        txt_lay = QVBoxLayout()
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter text here...")
        self.text_input.setMaximumHeight(80)
        self.text_input.textChanged.connect(self._update_preview)
        txt_lay.addWidget(self.text_input)
        txt_grp.setLayout(txt_lay)
        layout.addWidget(txt_grp)
        
        font_grp = QGroupBox("Font")
        font_lay = QVBoxLayout()
        
        type_lay = QHBoxLayout()
        type_lay.addWidget(QLabel("Font:"))
        self.font_cb = QComboBox()
        self.font_cb.addItems([
            "SIMPLEX", "PLAIN", "DUPLEX", "COMPLEX",
            "TRIPLEX", "SCRIPT_SIMPLEX", "SCRIPT_COMPLEX"
        ])
        self.font_cb.currentIndexChanged.connect(self._update_preview)
        type_lay.addWidget(self.font_cb)
        font_lay.addLayout(type_lay)
        
        size_lay = QHBoxLayout()
        size_lay.addWidget(QLabel("Size:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 10)
        self.size_spin.setValue(2)
        self.size_spin.valueChanged.connect(self._update_preview)
        size_lay.addWidget(self.size_spin)
        font_lay.addLayout(size_lay)
        
        thick_lay = QHBoxLayout()
        thick_lay.addWidget(QLabel("Thickness:"))
        self.thick_spin = QSpinBox()
        self.thick_spin.setRange(1, 10)
        self.thick_spin.setValue(2)
        self.thick_spin.valueChanged.connect(self._update_preview)
        thick_lay.addWidget(self.thick_spin)
        font_lay.addLayout(thick_lay)
        
        font_grp.setLayout(font_lay)
        layout.addWidget(font_grp)
        
        color_grp = QGroupBox("Color")
        color_lay = QVBoxLayout()
        
        txt_color_lay = QHBoxLayout()
        txt_color_lay.addWidget(QLabel("Text Color:"))
        self.txt_color_btn = QPushButton("Select")
        self.txt_color_btn.clicked.connect(self._select_text_color)
        self.txt_color_box = QLabel()
        self.txt_color_box.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        self.txt_color_box.setMinimumSize(30, 20)
        txt_color_lay.addWidget(self.txt_color_btn)
        txt_color_lay.addWidget(self.txt_color_box)
        color_lay.addLayout(txt_color_lay)
        
        self.bg_chk = QCheckBox("Add Background")
        self.bg_chk.stateChanged.connect(self._update_preview)
        color_lay.addWidget(self.bg_chk)
        
        bg_color_lay = QHBoxLayout()
        bg_color_lay.addWidget(QLabel("Background:"))
        self.bg_color_btn = QPushButton("Select")
        self.bg_color_btn.clicked.connect(self._select_bg_color)
        self.bg_color_btn.setEnabled(False)
        self.bg_color_box = QLabel()
        self.bg_color_box.setStyleSheet("background-color: black; border: 1px solid #ccc;")
        self.bg_color_box.setMinimumSize(30, 20)
        bg_color_lay.addWidget(self.bg_color_btn)
        bg_color_lay.addWidget(self.bg_color_box)
        color_lay.addLayout(bg_color_lay)
        
        self.bg_chk.stateChanged.connect(lambda: self.bg_color_btn.setEnabled(self.bg_chk.isChecked()))
        
        color_grp.setLayout(color_lay)
        layout.addWidget(color_grp)
        
        prev_grp = QGroupBox("Preview")
        prev_lay = QVBoxLayout()
        self.preview = QLabel("Sample Text")
        self.preview.setMinimumHeight(100)
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setStyleSheet("background-color: #2a2a2a; color: white; padding: 20px; font-size: 16px;")
        prev_lay.addWidget(self.preview)
        prev_grp.setLayout(prev_lay)
        layout.addWidget(prev_grp)
        
        btn_lay = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        btn_lay.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_lay.addWidget(cancel_btn)
        layout.addLayout(btn_lay)
        
    def _select_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_color = (color.blue(), color.green(), color.red())
            self.txt_color_box.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
            self._update_preview()
            
    def _select_bg_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.bg_color = (color.blue(), color.green(), color.red())
            self.bg_color_box.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
            self._update_preview()
            
    def _update_preview(self):
        text = self.text_input.toPlainText() or "Sample"
        size = self.size_spin.value()
        
        style = f"font-size: {12 + size * 2}px; font-family: Tahoma, Arial;"
        if self.bg_chk.isChecked() and self.bg_color:
            r, g, b = self.bg_color[2], self.bg_color[1], self.bg_color[0]
            style += f" background-color: rgb({r},{g},{b});"
        else:
            style += " background-color: #2a2a2a;"
            
        r, g, b = self.text_color[2], self.text_color[1], self.text_color[0]
        style += f" color: rgb({r},{g},{b}); padding: 20px;"
        
        self.preview.setStyleSheet(style)
        self.preview.setText(text)
        
    def _get_font(self):
        fonts = {
            "SIMPLEX": cv2.FONT_HERSHEY_SIMPLEX,
            "PLAIN": cv2.FONT_HERSHEY_PLAIN,
            "DUPLEX": cv2.FONT_HERSHEY_DUPLEX,
            "COMPLEX": cv2.FONT_HERSHEY_COMPLEX,
            "TRIPLEX": cv2.FONT_HERSHEY_TRIPLEX,
            "SCRIPT_SIMPLEX": cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
            "SCRIPT_COMPLEX": cv2.FONT_HERSHEY_SCRIPT_COMPLEX
        }
        return fonts.get(self.font_cb.currentText(), cv2.FONT_HERSHEY_SIMPLEX)
        
    def get_settings(self):
        text = self.text_input.toPlainText()
        return {
            'text': text,
            'font': self._get_font(),
            'scale': self.size_spin.value() / 2.0,
            'color': self.text_color,
            'thickness': self.thick_spin.value(),
            'has_background': self.bg_chk.isChecked(),
            'bg_color': self.bg_color if self.bg_chk.isChecked() else None,
            'is_persian': self._has_persian(text)
        }
        
    def _has_persian(self, text):
        persian = set('آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی')
        return any(c in persian for c in text)
