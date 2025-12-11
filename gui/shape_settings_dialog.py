from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSpinBox, QComboBox, QGroupBox, 
                             QColorDialog, QCheckBox)


class ShapeSettingsDialog(QDialog):
    def __init__(self, shape_type, parent=None):
        super().__init__(parent)
        self.shape = shape_type
        self.setWindowTitle(f"{shape_type.title()} Settings")
        self.setGeometry(300, 300, 400, 400)
        self.line_color = (0, 255, 0)
        self.fill_color = (255, 0, 0)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        thick_grp = QGroupBox("Line Thickness")
        thick_lay = QHBoxLayout()
        self.thick_spin = QSpinBox()
        self.thick_spin.setRange(1, 20)
        self.thick_spin.setValue(3)
        thick_lay.addWidget(QLabel("Thickness:"))
        thick_lay.addWidget(self.thick_spin)
        thick_grp.setLayout(thick_lay)
        layout.addWidget(thick_grp)
        
        line_grp = QGroupBox("Line Color")
        line_lay = QHBoxLayout()
        self.line_btn = QPushButton("Select")
        self.line_btn.clicked.connect(self._select_line)
        self.line_box = QLabel()
        self.line_box.setStyleSheet("background-color: lime; border: 1px solid #ccc;")
        self.line_box.setMinimumSize(30, 20)
        line_lay.addWidget(self.line_btn)
        line_lay.addWidget(self.line_box)
        line_grp.setLayout(line_lay)
        layout.addWidget(line_grp)
        
        fill_grp = QGroupBox("Fill")
        fill_lay = QVBoxLayout()
        self.fill_chk = QCheckBox("Fill Shape")
        fill_lay.addWidget(self.fill_chk)
        
        fill_color_lay = QHBoxLayout()
        self.fill_btn = QPushButton("Fill Color")
        self.fill_btn.clicked.connect(self._select_fill)
        self.fill_btn.setEnabled(False)
        self.fill_box = QLabel()
        self.fill_box.setStyleSheet("background-color: red; border: 1px solid #ccc;")
        self.fill_box.setMinimumSize(30, 20)
        fill_color_lay.addWidget(self.fill_btn)
        fill_color_lay.addWidget(self.fill_box)
        fill_lay.addLayout(fill_color_lay)
        
        self.fill_chk.stateChanged.connect(lambda: self.fill_btn.setEnabled(self.fill_chk.isChecked()))
        
        fill_grp.setLayout(fill_lay)
        layout.addWidget(fill_grp)
        
        type_grp = QGroupBox("Line Type")
        type_lay = QHBoxLayout()
        self.type_cb = QComboBox()
        self.type_cb.addItems(["Solid", "Dashed", "Dotted"])
        type_lay.addWidget(self.type_cb)
        type_grp.setLayout(type_lay)
        layout.addWidget(type_grp)
        
        layout.addStretch()
        
        btn_lay = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        btn_lay.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_lay.addWidget(cancel_btn)
        layout.addLayout(btn_lay)
        
    def _select_line(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.line_color = (color.blue(), color.green(), color.red())
            self.line_box.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
            
    def _select_fill(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.fill_color = (color.blue(), color.green(), color.red())
            self.fill_box.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
            
    def get_settings(self):
        return {
            'thickness': self.thick_spin.value() if not self.fill_chk.isChecked() else -1,
            'line_color': self.line_color,
            'fill': self.fill_chk.isChecked(),
            'fill_color': self.fill_color if self.fill_chk.isChecked() else None,
            'line_type': self.type_cb.currentIndex()
        }
