from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSlider, QLabel
from PyQt5.QtCore import Qt, pyqtSignal


class ZoomWidget(QWidget):
    zoom_changed = pyqtSignal(int)
    fit_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__()
        self.level = 100
        self.setStyleSheet("""
            QWidget {
                background-color: #333333;
                border-top: 1px solid #404040;
            }
        """)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)
        
        # دکمه Fit
        fit_btn = QPushButton("⊡")
        fit_btn.setToolTip("اندازه پنجره")
        fit_btn.setFixedSize(28, 28)
        fit_btn.setStyleSheet("font-size: 14px;")
        fit_btn.clicked.connect(lambda: self.slider.setValue(100))
        layout.addWidget(fit_btn)
        
        # دکمه کوچک‌نمایی
        out_btn = QPushButton("−")
        out_btn.setToolTip("کوچک‌نمایی")
        out_btn.setFixedSize(28, 28)
        out_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        out_btn.clicked.connect(self._zoom_out)
        layout.addWidget(out_btn)
        
        # اسلایدر
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(10, 400)
        self.slider.setValue(100)
        self.slider.setFixedWidth(150)
        self.slider.valueChanged.connect(self._on_change)
        layout.addWidget(self.slider)
        
        # دکمه بزرگ‌نمایی
        in_btn = QPushButton("+")
        in_btn.setToolTip("بزرگ‌نمایی")
        in_btn.setFixedSize(28, 28)
        in_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        in_btn.clicked.connect(self._zoom_in)
        layout.addWidget(in_btn)
        
        # درصد زوم
        self.label = QLabel("100%")
        self.label.setFixedWidth(50)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: #0078d4; font-weight: bold;")
        layout.addWidget(self.label)
        
        layout.addStretch()
        
        # دکمه 1:1
        actual_btn = QPushButton("1:1")
        actual_btn.setToolTip("اندازه واقعی")
        actual_btn.setFixedSize(36, 28)
        actual_btn.clicked.connect(self._reset)
        layout.addWidget(actual_btn)
        
        # دکمه 50%
        half_btn = QPushButton("50%")
        half_btn.setToolTip("نصف اندازه")
        half_btn.setFixedSize(36, 28)
        half_btn.clicked.connect(lambda: self.slider.setValue(50))
        layout.addWidget(half_btn)
        
        # دکمه 200%
        double_btn = QPushButton("200%")
        double_btn.setToolTip("دو برابر")
        double_btn.setFixedSize(42, 28)
        double_btn.clicked.connect(lambda: self.slider.setValue(200))
        layout.addWidget(double_btn)
        
    def _zoom_in(self):
        self.slider.setValue(min(200, self.slider.value() + 10))
        
    def _zoom_out(self):
        self.slider.setValue(max(10, self.slider.value() - 10))
        
    def _reset(self):
        self.slider.setValue(100)
        
    def _on_change(self, val):
        self.level = val
        self.label.setText(f"{val}%")
        self.zoom_changed.emit(val)
        
    def get_level(self):
        return self.level
