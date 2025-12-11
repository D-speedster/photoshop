from PyQt5.QtWidgets import QToolBar, QAction, QWidget, QSizePolicy
from PyQt5.QtCore import Qt


class Toolbar(QToolBar):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.setMovable(False)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setIconSize(self.iconSize())
        self.setStyleSheet("""
            QToolBar {
                background-color: #3c3c3c;
                border: none;
                border-bottom: 1px solid #1a1a1a;
                spacing: 2px;
                padding: 2px 4px;
            }
            QToolBar::separator {
                background-color: #1a1a1a;
                width: 1px;
                margin: 4px 3px;
            }
            QToolButton {
                background-color: transparent;
                color: #e8e8e8;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 15px;
                min-width: 28px;
                min-height: 28px;
            }
            QToolButton:hover {
                background-color: #4a4a4a;
            }
            QToolButton:pressed {
                background-color: #2d8ceb;
            }
        """)
        self._setup_actions()
        
    def _setup_actions(self):
        # تشخیص چهره (اول چون RTL هست)
        self._add_action("👤", "تشخیص چهره", "Ctrl+F", self.main.open_face_detection)
        
        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.addWidget(spacer)
        
        # مقایسه
        self._add_action("📦", "پردازش دسته‌ای", None, self.main.open_batch_processing)
        self._add_action("⚖", "مقایسه", "Ctrl+B", self.main.show_comparison)
        
        self.addSeparator()
        
        # ابزارها
        self._add_action("📊", "هیستوگرام", None, self.main.show_histogram)
        self._add_action("📐", "تغییر اندازه", None, self.main.resize_image)
        self._add_action("✂", "برش", "Ctrl+X", self.main.crop_image)
        
        self.addSeparator()
        
        # چرخش
        self._add_action("↕", "آینه عمودی", None, lambda: self.main.flip_image("vertical"))
        self._add_action("↔", "آینه افقی", None, lambda: self.main.flip_image("horizontal"))
        self._add_action("↷", "چرخش راست", None, lambda: self.main.rotate_image(90))
        self._add_action("↶", "چرخش چپ", None, lambda: self.main.rotate_image(-90))
        
        self.addSeparator()
        
        # دوربین
        self._add_action("📷", "دوربین", None, self.main.open_camera)
        
        self.addSeparator()
        
        # ویرایش
        self._add_action("↪", "جلو", "Ctrl+Y", self.main.redo)
        self._add_action("↩", "بازگشت", "Ctrl+Z", self.main.undo)
        
        self.addSeparator()
        
        # فایل
        self._add_action("💾", "ذخیره", "Ctrl+S", self.main.save_image)
        self._add_action("📂", "باز کردن", "Ctrl+O", self.main.open_image)
        
    def _add_action(self, icon, tooltip, shortcut, callback):
        action = QAction(icon, self)
        action.setToolTip(tooltip)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(callback)
        self.addAction(action)
        return action
