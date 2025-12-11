from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QButtonGroup, QFrame
from PyQt5.QtCore import pyqtSignal, Qt


class IconToolbar(QWidget):
    tool_selected = pyqtSignal(str)
    
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.setFixedWidth(54)
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                border-left: 1px solid #404040;
            }
        """)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(3)
        layout.setContentsMargins(6, 10, 6, 10)
        
        self.btn_grp = QButtonGroup()
        self.btn_grp.setExclusive(False)
        
        # گروه فایل
        file_tools = [
            ("📂", "open", "باز کردن (Ctrl+O)"),
            ("💾", "save", "ذخیره (Ctrl+S)"),
            ("📷", "camera", "دوربین"),
        ]
        self._add_group(layout, file_tools)
        
        self._add_separator(layout)
        
        # گروه ویرایش
        edit_tools = [
            ("↩", "undo", "برگشت (Ctrl+Z)"),
            ("↪", "redo", "جلو (Ctrl+Y)"),
        ]
        self._add_group(layout, edit_tools)
        
        self._add_separator(layout)
        
        # گروه تبدیل
        transform_tools = [
            ("✂", "crop", "برش"),
            ("📐", "resize", "تغییر اندازه"),
            ("↷", "rotate_right", "چرخش راست"),
            ("↶", "rotate_left", "چرخش چپ"),
            ("↔", "flip_h", "آینه افقی"),
            ("↕", "flip_v", "آینه عمودی"),
        ]
        self._add_group(layout, transform_tools)
        
        self._add_separator(layout)
        
        # گروه تحلیل
        analysis_tools = [
            ("📊", "histogram", "هیستوگرام"),
            ("⚖", "compare", "مقایسه"),
        ]
        self._add_group(layout, analysis_tools)
            
        layout.addStretch()
        
    def _add_group(self, layout, tools):
        for icon, tid, tip in tools:
            btn = self._create_btn(icon, tid, tip)
            layout.addWidget(btn)
            
    def _add_separator(self, layout):
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #404040; margin: 4px 0;")
        layout.addWidget(sep)
        
    def _create_btn(self, icon, tid, tip):
        btn = QPushButton(icon)
        btn.setToolTip(tip)
        btn.setFixedSize(40, 40)
        btn.setStyleSheet("""
            QPushButton {
                font-size: 17px;
                padding: 0;
                background-color: #383838;
                border: 1px solid #404040;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #454545;
                border: 1px solid #0078d4;
            }
            QPushButton:pressed {
                background-color: #0078d4;
            }
        """)
        btn.clicked.connect(lambda _, t=tid: self._on_click(t))
        self.btn_grp.addButton(btn)
        return btn
        
    def _on_click(self, tid):
        self.tool_selected.emit(tid)
        
        actions = {
            "open": self.main.open_image,
            "save": self.main.save_image,
            "camera": self.main.open_camera,
            "undo": self.main.undo,
            "redo": self.main.redo,
            "crop": self.main.crop_image,
            "resize": self.main.resize_image,
            "rotate_right": lambda: self.main.rotate_image(90),
            "rotate_left": lambda: self.main.rotate_image(-90),
            "flip_h": lambda: self.main.flip_image("horizontal"),
            "flip_v": lambda: self.main.flip_image("vertical"),
            "histogram": self.main.show_histogram,
            "compare": self.main.show_comparison,
        }
        
        if tid in actions:
            actions[tid]()
