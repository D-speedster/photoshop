from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QGroupBox, QComboBox, QMessageBox, QColorDialog)
from PyQt5.QtCore import Qt, QRect, pyqtSignal
import cv2


class SelectionState:
    def __init__(self):
        self.selecting = False
        self.rect = None
        self.start = None
        self.end = None
        self.mode = "rectangle"
        
    def begin(self, point):
        self.selecting = True
        self.start = point
        self.end = point
        
    def update(self, point):
        if self.selecting:
            self.end = point
            
    def finish(self):
        if self.selecting and self.start and self.end:
            x1 = min(self.start.x(), self.end.x())
            y1 = min(self.start.y(), self.end.y())
            x2 = max(self.start.x(), self.end.x())
            y2 = max(self.start.y(), self.end.y())
            self.rect = QRect(x1, y1, x2 - x1, y2 - y1)
            self.selecting = False
            return self.rect
        return None
        
    def clear(self):
        self.selecting = False
        self.rect = None
        self.start = None
        self.end = None
        
    def has_selection(self):
        return self.rect is not None


class SelectionTool(QWidget):
    selection_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.state = SelectionState()
        self.copied = None
        self.setLayoutDirection(Qt.RightToLeft)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # گروه انتخاب
        sel_grp = QGroupBox("انتخاب ناحیه")
        sel_grp.setLayoutDirection(Qt.RightToLeft)
        sel_grp.setAlignment(Qt.AlignRight)
        sel_grp.setStyleSheet("""
            QGroupBox {
                font-size: 10px;
                font-weight: normal;
                color: #9a9a9a;
                border: 1px solid #1a1a1a;
                border-radius: 0px;
                margin-top: 10px;
                padding: 4px 2px 2px 2px;
                background-color: #3c3c3c;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                right: 5px;
                top: 0px;
                padding: 0 3px;
                background-color: #3c3c3c;
            }
        """)
        sel_lay = QVBoxLayout()
        sel_lay.setSpacing(2)
        
        mode_lay = QHBoxLayout()
        mode_lbl = QLabel("حالت:")
        mode_lbl.setAlignment(Qt.AlignRight)
        mode_lay.addWidget(mode_lbl)
        self.mode_cb = QComboBox()
        self.mode_cb.addItems(["مستطیل", "بیضی", "آزاد"])
        self.mode_cb.currentIndexChanged.connect(self._change_mode)
        mode_lay.addWidget(self.mode_cb)
        sel_lay.addLayout(mode_lay)
        
        self.sel_btn = QPushButton("فعال کردن انتخاب")
        self.sel_btn.setCheckable(True)
        self.sel_btn.setMaximumHeight(24)
        self.sel_btn.setStyleSheet("font-size: 10px;")
        self.sel_btn.clicked.connect(self._toggle_mode)
        sel_lay.addWidget(self.sel_btn)
        
        self.info_label = QLabel("انتخاب: -")
        self.info_label.setAlignment(Qt.AlignRight)
        self.info_label.setStyleSheet("font-size: 10px; color: #888;")
        sel_lay.addWidget(self.info_label)
        
        sel_grp.setLayout(sel_lay)
        layout.addWidget(sel_grp)
        
        # گروه عملیات
        ops_grp = QGroupBox("عملیات")
        ops_grp.setLayoutDirection(Qt.RightToLeft)
        ops_grp.setAlignment(Qt.AlignRight)
        ops_grp.setStyleSheet("""
            QGroupBox {
                font-size: 10px;
                font-weight: normal;
                color: #9a9a9a;
                border: 1px solid #1a1a1a;
                border-radius: 0px;
                margin-top: 10px;
                padding: 4px 2px 2px 2px;
                background-color: #3c3c3c;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                right: 5px;
                top: 0px;
                padding: 0 3px;
                background-color: #3c3c3c;
            }
        """)
        ops_lay = QVBoxLayout()
        ops_lay.setSpacing(2)
        
        ops = [
            ("برش ناحیه", self._crop),
            ("کپی", self._copy),
            ("پر کردن با رنگ", self._fill),
            ("محو کردن", self._blur),
            ("معکوس رنگ", self._invert),
            ("پاک کردن انتخاب", self._clear),
        ]
        
        for name, func in ops:
            btn = QPushButton(name)
            btn.setMaximumHeight(22)
            btn.setStyleSheet("font-size: 10px; padding: 1px 3px;")
            btn.clicked.connect(func)
            ops_lay.addWidget(btn)
        
        ops_grp.setLayout(ops_lay)
        layout.addWidget(ops_grp)
        
    def _toggle_mode(self, checked):
        if self.parent_window is None or self.parent_window.current_image is None:
            if checked:
                QMessageBox.warning(self, "خطا", "ابتدا یک تصویر باز کنید")
                self.sel_btn.setChecked(False)
            return
            
        if checked:
            self.sel_btn.setText("غیرفعال کردن")
            self.parent_window.image_label.setCursor(Qt.CrossCursor)
            self.parent_window.image_label.selection_tool = self
            self.parent_window.image_label.active_mode = 'selection'
        else:
            self.sel_btn.setText("فعال کردن انتخاب")
            self.parent_window.image_label.setCursor(Qt.ArrowCursor)
            self.parent_window.image_label.selection_tool = None
            self.parent_window.image_label.active_mode = None
            
    def _change_mode(self, idx):
        modes = ["rectangle", "ellipse", "free"]
        self.state.mode = modes[idx]
        
    def handle_mouse_press(self, pos):
        self.state.begin(pos)
            
    def handle_mouse_move(self, pos):
        if self.state.selecting:
            self.state.update(pos)
            
    def handle_mouse_release(self, pos):
        rect = self.state.finish()
        if rect:
            self.info_label.setText(f"انتخاب: {rect.width()}x{rect.height()}")
            self.sel_btn.setChecked(False)
            self._toggle_mode(False)
            
    def _get_coords(self):
        if not self.state.has_selection():
            QMessageBox.warning(self, "خطا", "ابتدا یک ناحیه انتخاب کنید")
            return None
            
        if self.parent_window is None or self.parent_window.current_image is None:
            QMessageBox.warning(self, "خطا", "تصویری وجود ندارد")
            return None
            
        rect = self.state.rect
        label = self.parent_window.image_label
        img = self.parent_window.current_image
        img_h, img_w = img.shape[:2]
        
        scale_w = img_w / label.size().width()
        scale_h = img_h / label.size().height()
        scale = max(scale_w, scale_h)
        
        x1 = max(0, min(int(rect.x() * scale), img_w))
        y1 = max(0, min(int(rect.y() * scale), img_h))
        x2 = max(0, min(int((rect.x() + rect.width()) * scale), img_w))
        y2 = max(0, min(int((rect.y() + rect.height()) * scale), img_h))
        
        if x2 <= x1 or y2 <= y1:
            QMessageBox.warning(self, "خطا", "ناحیه انتخابی نامعتبر است")
            return None
            
        return (x1, y1, x2, y2)
        
    def _crop(self):
        coords = self._get_coords()
        if coords:
            x1, y1, x2, y2 = coords
            cropped = self.parent_window.current_image[y1:y2, x1:x2]
            if cropped.size > 0:
                self.parent_window.current_image = cropped
                self.parent_window.history.add_state(cropped.copy())
                self.parent_window.display_image(cropped)
                self.parent_window.info_panel.update_info(cropped)
                self._clear()
            
    def _copy(self):
        coords = self._get_coords()
        if coords:
            x1, y1, x2, y2 = coords
            self.copied = self.parent_window.current_image[y1:y2, x1:x2].copy()
            QMessageBox.information(self, "انجام شد", "ناحیه کپی شد")
            
    def _fill(self):
        coords = self._get_coords()
        if coords:
            color = QColorDialog.getColor()
            if color.isValid():
                x1, y1, x2, y2 = coords
                bgr = (color.blue(), color.green(), color.red())
                img = self.parent_window.current_image.copy()
                img[y1:y2, x1:x2] = bgr
                self.parent_window.current_image = img
                self.parent_window.history.add_state(img.copy())
                self.parent_window.display_image(img)
                self._clear()
                
    def _blur(self):
        coords = self._get_coords()
        if coords:
            x1, y1, x2, y2 = coords
            img = self.parent_window.current_image.copy()
            region = img[y1:y2, x1:x2]
            blurred = cv2.GaussianBlur(region, (21, 21), 0)
            img[y1:y2, x1:x2] = blurred
            self.parent_window.current_image = img
            self.parent_window.history.add_state(img.copy())
            self.parent_window.display_image(img)
            self._clear()
            
    def _invert(self):
        coords = self._get_coords()
        if coords:
            x1, y1, x2, y2 = coords
            img = self.parent_window.current_image.copy()
            region = img[y1:y2, x1:x2]
            img[y1:y2, x1:x2] = cv2.bitwise_not(region)
            self.parent_window.current_image = img
            self.parent_window.history.add_state(img.copy())
            self.parent_window.display_image(img)
            self._clear()
            
    def _clear(self):
        self.state.clear()
        self.info_label.setText("انتخاب: -")
        if self.sel_btn.isChecked():
            self.sel_btn.setChecked(False)
            self._toggle_mode(False)
