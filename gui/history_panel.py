from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget, 
                             QListWidgetItem, QGroupBox, QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon


class HistoryPanel(QWidget):
    state_selected = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setMaximumWidth(170)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # لیست تاریخچه
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: #353535;
                border: 1px solid #404040;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 4px 8px;
                border-bottom: 1px solid #404040;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
            }
        """)
        self.history_list.itemClicked.connect(self._on_item_click)
        layout.addWidget(self.history_list)
        
        # دکمه‌ها
        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(4)
        
        self.undo_btn = QPushButton("↩")
        self.undo_btn.setToolTip("برگشت")
        self.undo_btn.setFixedSize(28, 28)
        self.undo_btn.clicked.connect(self._undo)
        btn_lay.addWidget(self.undo_btn)
        
        self.redo_btn = QPushButton("↪")
        self.redo_btn.setToolTip("جلو")
        self.redo_btn.setFixedSize(28, 28)
        self.redo_btn.clicked.connect(self._redo)
        btn_lay.addWidget(self.redo_btn)
        
        btn_lay.addStretch()
        
        self.clear_btn = QPushButton("🗑")
        self.clear_btn.setToolTip("پاک کردن تاریخچه")
        self.clear_btn.setFixedSize(28, 28)
        self.clear_btn.clicked.connect(self._clear)
        btn_lay.addWidget(self.clear_btn)
        
        layout.addLayout(btn_lay)
        
        # اضافه کردن حالت اولیه
        self._add_state("باز کردن تصویر")
        
    def _add_state(self, action_name):
        item = QListWidgetItem(f"• {action_name}")
        self.history_list.addItem(item)
        self.history_list.setCurrentItem(item)
        
    def add_action(self, action_name):
        # حذف آیتم‌های بعد از موقعیت فعلی
        current = self.history_list.currentRow()
        while self.history_list.count() > current + 1:
            self.history_list.takeItem(current + 1)
        
        self._add_state(action_name)
        
        # محدود کردن به 20 آیتم
        while self.history_list.count() > 20:
            self.history_list.takeItem(0)
            
    def _on_item_click(self, item):
        idx = self.history_list.row(item)
        self.state_selected.emit(idx)
        
    def _undo(self):
        if self.main_window:
            self.main_window.undo()
            current = self.history_list.currentRow()
            if current > 0:
                self.history_list.setCurrentRow(current - 1)
            
    def _redo(self):
        if self.main_window:
            self.main_window.redo()
            current = self.history_list.currentRow()
            if current < self.history_list.count() - 1:
                self.history_list.setCurrentRow(current + 1)
            
    def _clear(self):
        self.history_list.clear()
        self._add_state("باز کردن تصویر")
        
    def reset(self):
        self.history_list.clear()
        self._add_state("باز کردن تصویر")
