from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QSlider, QGroupBox, QScrollArea, QMessageBox,
                             QFrame, QHBoxLayout)
from PyQt5.QtCore import Qt


class Sidebar(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.setMaximumWidth(210)
        self.setMinimumWidth(190)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                border-left: 1px solid #404040;
            }
        """)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none;")
        scroll_widget = QWidget()
        scroll_widget.setLayoutDirection(Qt.RightToLeft)
        scroll_lay = QVBoxLayout(scroll_widget)
        scroll_lay.setSpacing(8)
        scroll_lay.setContentsMargins(8, 8, 8, 8)
        
        # تنظیمات تصویر
        adj_grp = self._create_group("تنظیمات")
        adj_lay = QVBoxLayout()
        adj_lay.setSpacing(3)
        
        self.bright_label = QLabel("روشنایی")
        self.bright_label.setAlignment(Qt.AlignRight)
        self.bright_slider = self._create_slider()
        self.bright_slider.sliderPressed.connect(lambda: self._start_adj("brightness"))
        self.bright_slider.valueChanged.connect(lambda v: self._preview_adj("brightness", v))
        self.bright_slider.sliderReleased.connect(lambda: self._finish_adj("brightness"))
        adj_lay.addWidget(self.bright_label)
        adj_lay.addWidget(self.bright_slider)
        
        self.contrast_label = QLabel("کنتراست")
        self.contrast_label.setAlignment(Qt.AlignRight)
        self.contrast_slider = self._create_slider()
        self.contrast_slider.sliderPressed.connect(lambda: self._start_adj("contrast"))
        self.contrast_slider.valueChanged.connect(lambda v: self._preview_adj("contrast", v))
        self.contrast_slider.sliderReleased.connect(lambda: self._finish_adj("contrast"))
        adj_lay.addWidget(self.contrast_label)
        adj_lay.addWidget(self.contrast_slider)
        
        self.sat_label = QLabel("اشباع رنگ")
        self.sat_label.setAlignment(Qt.AlignRight)
        self.sat_slider = self._create_slider()
        self.sat_slider.sliderPressed.connect(lambda: self._start_adj("saturation"))
        self.sat_slider.valueChanged.connect(lambda v: self._preview_adj("saturation", v))
        self.sat_slider.sliderReleased.connect(lambda: self._finish_adj("saturation"))
        adj_lay.addWidget(self.sat_label)
        adj_lay.addWidget(self.sat_slider)
        
        reset_btn = QPushButton("بازنشانی")
        reset_btn.clicked.connect(self._reset_adj)
        adj_lay.addWidget(reset_btn)
        
        adj_grp.setLayout(adj_lay)
        scroll_lay.addWidget(adj_grp)
        
        # فیلترها
        filter_grp = self._create_group("فیلترها")
        filter_lay = QVBoxLayout()
        filter_lay.setSpacing(2)
        
        row1 = QHBoxLayout()
        for name, fid in [("محو", "blur"), ("میانه", "median"), ("شارپ", "sharpen")]:
            btn = self._create_small_btn(name)
            btn.clicked.connect(lambda _, f=fid: self._apply_filter(f))
            row1.addWidget(btn)
        filter_lay.addLayout(row1)
        
        row2 = QHBoxLayout()
        for name, fid in [("لبه", "edge"), ("برجسته", "emboss"), ("خاکستری", "grayscale")]:
            btn = self._create_small_btn(name)
            btn.clicked.connect(lambda _, f=fid: self._apply_filter(f))
            row2.addWidget(btn)
        filter_lay.addLayout(row2)
        
        row3 = QHBoxLayout()
        for name, fid in [("سپیا", "sepia"), ("معکوس", "invert"), ("کارتون", "cartoon")]:
            btn = self._create_small_btn(name)
            btn.clicked.connect(lambda _, f=fid: self._apply_filter(f))
            row3.addWidget(btn)
        filter_lay.addLayout(row3)
        
        filter_grp.setLayout(filter_lay)
        scroll_lay.addWidget(filter_grp)
        
        # کانال‌های رنگی
        channel_grp = self._create_group("کانال‌ها")
        channel_lay = QVBoxLayout()
        channel_lay.setSpacing(2)
        
        ch_row1 = QHBoxLayout()
        for name, fid, color in [("- قرمز", "remove_red", "#ef4444"), 
                                  ("- سبز", "remove_green", "#22c55e"), 
                                  ("- آبی", "remove_blue", "#3b82f6")]:
            btn = self._create_small_btn(name)
            btn.setStyleSheet(f"QPushButton {{ border-left: 3px solid {color}; }}")
            btn.clicked.connect(lambda _, f=fid: self._apply_filter(f))
            ch_row1.addWidget(btn)
        channel_lay.addLayout(ch_row1)
        
        ch_row2 = QHBoxLayout()
        for name, fid, color in [("قرمز", "only_red", "#ef4444"), 
                                  ("سبز", "only_green", "#22c55e"), 
                                  ("آبی", "only_blue", "#3b82f6")]:
            btn = self._create_small_btn(name)
            btn.setStyleSheet(f"QPushButton {{ border-left: 3px solid {color}; }}")
            btn.clicked.connect(lambda _, f=fid: self._apply_filter(f))
            ch_row2.addWidget(btn)
        channel_lay.addLayout(ch_row2)
        
        channel_grp.setLayout(channel_lay)
        scroll_lay.addWidget(channel_grp)
        
        # ابزارهای رسم
        draw_grp = self._create_group("رسم")
        draw_lay = QVBoxLayout()
        draw_lay.setSpacing(2)
        
        draw_row = QHBoxLayout()
        for name, tid in [("خط", "line"), ("مستطیل", "rectangle"), ("دایره", "circle"), ("بیضی", "ellipse")]:
            btn = self._create_small_btn(name)
            btn.clicked.connect(lambda _, t=tid: self._select_tool(t))
            draw_row.addWidget(btn)
        draw_lay.addLayout(draw_row)
        
        text_btn = self._create_small_btn("متن")
        text_btn.clicked.connect(lambda: self._select_tool("text"))
        draw_lay.addWidget(text_btn)
        
        draw_grp.setLayout(draw_lay)
        scroll_lay.addWidget(draw_grp)
        
        # ابزار انتخاب (Selection Tool)
        from gui.selection_tool import SelectionTool
        self.selection = SelectionTool(self.main)
        scroll_lay.addWidget(self.selection)
        
        # عملیات تصویر
        ops_grp = self._create_group("عملیات")
        ops_lay = QVBoxLayout()
        ops_lay.setSpacing(2)
        
        ops = [
            ("ادغام تصاویر", self.main.open_blend_dialog),
            ("رنگی/خاکستری", self.main.open_split_view),
            ("چرخش آزاد", self.main.open_rotate_dialog),
            ("ساخت شکل", self.main.open_shape_generator),
        ]
        for name, func in ops:
            btn = self._create_small_btn(name)
            btn.clicked.connect(func)
            ops_lay.addWidget(btn)
        
        ops_grp.setLayout(ops_lay)
        scroll_lay.addWidget(ops_grp)
        
        # تشخیص
        detect_grp = self._create_group("تشخیص")
        detect_lay = QVBoxLayout()
        detect_lay.setSpacing(2)
        
        detect_row = QHBoxLayout()
        corner_btn = self._create_small_btn("گوشه")
        corner_btn.clicked.connect(lambda: self._apply_filter("corners"))
        detect_row.addWidget(corner_btn)
        
        harris_btn = self._create_small_btn("Harris")
        harris_btn.clicked.connect(lambda: self._apply_filter("harris"))
        detect_row.addWidget(harris_btn)
        detect_lay.addLayout(detect_row)
        
        face_btn = self._create_small_btn("تشخیص چهره")
        face_btn.clicked.connect(self.main.open_face_detection)
        detect_lay.addWidget(face_btn)
        
        detect_grp.setLayout(detect_lay)
        scroll_lay.addWidget(detect_grp)
        
        # ویدیو
        video_grp = self._create_group("ویدیو")
        video_lay = QVBoxLayout()
        
        video_btn = self._create_small_btn("پردازش ویدیو")
        video_btn.clicked.connect(self.main.open_video_processor)
        video_lay.addWidget(video_btn)
        
        video_grp.setLayout(video_lay)
        scroll_lay.addWidget(video_grp)
        
        scroll_lay.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
    def _create_group(self, title):
        grp = QGroupBox(title)
        grp.setLayoutDirection(Qt.RightToLeft)
        grp.setAlignment(Qt.AlignRight)
        grp.setStyleSheet("""
            QGroupBox {
                font-size: 11px;
                font-weight: 500;
                color: #b0b0b0;
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 14px;
                padding: 10px 6px 6px 6px;
                background-color: #333333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                right: 8px;
                top: -6px;
                padding: 2px 6px;
                background-color: #333333;
                border-radius: 3px;
            }
        """)
        return grp
        
    def _create_slider(self):
        slider = QSlider(Qt.Horizontal)
        slider.setRange(-100, 100)
        slider.setValue(0)
        slider.setLayoutDirection(Qt.LeftToRight)
        return slider
        
    def _create_small_btn(self, text):
        btn = QPushButton(text)
        btn.setMinimumHeight(26)
        btn.setMaximumHeight(28)
        btn.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                padding: 4px 6px;
                background-color: #404040;
                border: 1px solid #505050;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border: 1px solid #0078d4;
            }
            QPushButton:pressed {
                background-color: #0078d4;
            }
        """)
        return btn
        
    def _apply_filter(self, name):
        self.main.apply_filter(name)
        
    def _start_adj(self, adj_type):
        self.main.start_live_adjustment()
        
    def _preview_adj(self, adj_type, value):
        labels = {
            "brightness": (self.bright_label, "روشنایی"),
            "contrast": (self.contrast_label, "کنتراست"),
            "saturation": (self.sat_label, "اشباع رنگ")
        }
        if adj_type in labels:
            lbl, name = labels[adj_type]
            lbl.setText(f"{name}: {value}")
        self.main.preview_adjustment(adj_type, value)
        
    def _finish_adj(self, adj_type):
        self.main.finish_live_adjustment()
        
    def _reset_adj(self):
        for slider, label, name in [
            (self.bright_slider, self.bright_label, "روشنایی"),
            (self.contrast_slider, self.contrast_label, "کنتراست"),
            (self.sat_slider, self.sat_label, "اشباع رنگ")
        ]:
            slider.setValue(0)
            label.setText(name)
        self.main.reset_to_base_image()
        
    def _select_tool(self, name):
        if self.main.current_image is None:
            QMessageBox.warning(self, "خطا", "ابتدا یک تصویر باز کنید")
            return
        self.main.image_label.set_tool(name)
