from PyQt5.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, 
                             QWidget, QFileDialog, QMessageBox, QScrollArea, 
                             QProgressDialog, QTabWidget)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
import cv2
import numpy as np

from gui.toolbar import Toolbar
from gui.sidebar import Sidebar
from gui.camera_window import CameraWindow
from gui.crop_dialog import CropDialog
from gui.resize_dialog import ResizeDialog
from gui.histogram_window import HistogramWindow
from gui.image_info_panel import ImageInfoPanel
from gui.export_dialog import ExportDialog
from gui.zoom_widget import ZoomWidget
from gui.comparison_window import ComparisonWindow
from gui.drawing_canvas import DrawingCanvas
from gui.icon_toolbar import IconToolbar
from gui.layers_panel import LayersPanel
from gui.color_picker_tool import ColorPickerTool
from gui.history_panel import HistoryPanel
from core.image_processor import ImageProcessor
from utils.constants import STYLES_PATH
from utils.file_handler import FileHandler
from utils.history import History
from utils.worker import Worker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo Editor")
        self.setGeometry(100, 100, 1400, 900)
        
        self.processor = ImageProcessor()
        self.file_handler = FileHandler()
        self.history = History(max_size=10)
        
        self.current_image = None
        self.original_image = None
        self.base_image = None
        self.current_path = None
        self.camera_win = None
        self.zoom_level = 100
        self.adjusting = False
        
        self._setup_ui()
        
    def _setup_ui(self):
        self._load_style()
        
        central = QWidget()
        self.setCentralWidget(central)
        
        main_lay = QHBoxLayout(central)
        main_lay.setSpacing(0)
        main_lay.setContentsMargins(0, 0, 0, 0)
        
        self.toolbar = Toolbar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        
        # پنل اطلاعات سمت چپ
        left_panel = QTabWidget()
        left_panel.setMaximumWidth(180)
        
        self.info_panel = ImageInfoPanel()
        left_panel.addTab(self.info_panel, "اطلاعات")
        
        self.history_panel = HistoryPanel(self)
        left_panel.addTab(self.history_panel, "تاریخچه")
        
        self.layers_panel = LayersPanel(self)
        left_panel.addTab(self.layers_panel, "لایه‌ها")
        
        self.color_picker = ColorPickerTool(self)
        left_panel.addTab(self.color_picker, "رنگ")
        
        main_lay.addWidget(left_panel)
        
        # بخش مرکزی
        center_lay = QVBoxLayout()
        center_lay.setSpacing(0)
        center_lay.setContentsMargins(0, 0, 0, 0)
        
        # Canvas با حاشیه
        self.scroll = QScrollArea()
        self.scroll.setStyleSheet("""
            QScrollArea {
                background-color: #1a1a1a;
                border: none;
            }
        """)
        self.image_label = DrawingCanvas(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            background-color: #252525;
            border: 2px solid #404040;
            border-radius: 4px;
            margin: 10px;
        """)
        self.scroll.setWidget(self.image_label)
        self.scroll.setWidgetResizable(True)
        center_lay.addWidget(self.scroll)
        
        self.zoom_widget = ZoomWidget()
        self.zoom_widget.zoom_changed.connect(self._on_zoom)
        center_lay.addWidget(self.zoom_widget)
        
        main_lay.addLayout(center_lay, stretch=1)
        
        # سایدبار ابزارها سمت راست
        self.sidebar = Sidebar(self)
        main_lay.addWidget(self.sidebar)
        
        # نوار ابزار آیکونی سمت راست
        self.icon_toolbar = IconToolbar(self)
        main_lay.addWidget(self.icon_toolbar)
        
        self._show_placeholder()
        
    def _load_style(self):
        try:
            with open(STYLES_PATH, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception:
            pass
        
    def _show_placeholder(self):
        self.image_label.setText("Open an image to start\nor use the camera")
        self.image_label.setStyleSheet("color: #888; font-size: 16px; background-color: #1e1e1e; padding: 40px;")
        
    def open_image(self):
        path = self.file_handler.open_file_dialog()
        if path:
            img = self.file_handler.load_image(path)
            if img is not None:
                self.current_image = img
                self.original_image = img.copy()
                self.current_path = path
                self.history.clear()
                self.history.add_state(img.copy())
                self.display_image(img)
                self.info_panel.update_info(img, path)
                
    def save_image(self):
        if self.current_image is None:
            QMessageBox.warning(self, "Error", "No image to save")
            return
        
        dialog = ExportDialog(self.current_image, self)
        if dialog.exec_():
            if dialog.output_path:
                QMessageBox.information(self, "Done", "Image saved successfully")
                self.current_path = dialog.output_path
                self.info_panel.update_info(self.current_image, dialog.output_path)
                
    def display_image(self, image):
        if image is None:
            return
            
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        
        if self.zoom_level != 100:
            scale = self.zoom_level / 100.0
            new_w, new_h = int(w * scale), int(h * scale)
            rgb = cv2.resize(rgb, (new_w, new_h))
            h, w = new_h, new_w
            
        qimg = QImage(rgb.tobytes(), w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        scaled = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled)
        self.image_label.setStyleSheet("")
        
    def apply_filter(self, filter_name, **params):
        if self.current_image is None:
            QMessageBox.warning(self, "Error", "Open an image first")
            return
            
        self.progress = QProgressDialog("Processing...", None, 0, 0, self)
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.show()
        
        self.worker = Worker(self.processor.apply_filter, self.current_image, filter_name, **params)
        self.worker.finished.connect(self._on_filter_done)
        self.worker.error.connect(self._on_filter_error)
        self.worker.start()
        
    def _on_filter_done(self, result):
        self.progress.close()
        if result is not None:
            self.current_image = result
            self.history.add_state(result.copy())
            self.display_image(result)
            
    def _on_filter_error(self, err):
        self.progress.close()
        QMessageBox.critical(self, "Error", f"Processing failed: {err[1]}")
            
    def start_live_adjustment(self):
        if self.current_image is None:
            return
        if not self.adjusting:
            self.base_image = self.current_image.copy()
            self.adjusting = True
            
    def preview_adjustment(self, adj_type, value):
        if self.base_image is None or not self.adjusting:
            return
        result = self.processor.apply_adjustment(self.base_image, adj_type, value)
        if result is not None:
            self.current_image = result
            self.display_image(result)
            
    def finish_live_adjustment(self):
        if self.adjusting and self.current_image is not None:
            self.history.add_state(self.current_image.copy())
            self.base_image = None
            self.adjusting = False
            
    def reset_to_base_image(self):
        if self.base_image is not None:
            self.current_image = self.base_image.copy()
            self.display_image(self.current_image)
            self.base_image = None
            self.adjusting = False
            
    def undo(self):
        prev = self.history.undo()
        if prev is not None:
            self.current_image = prev
            self.display_image(prev)
            
    def redo(self):
        next_state = self.history.redo()
        if next_state is not None:
            self.current_image = next_state
            self.display_image(next_state)
            
    def open_camera(self):
        if self.camera_win is None:
            self.camera_win = CameraWindow(self)
        self.camera_win.show()
        
    def set_camera_image(self, image):
        self.current_image = image
        self.original_image = image.copy()
        self.history.clear()
        self.history.add_state(image.copy())
        self.display_image(image)
        self.info_panel.update_info(image)
        
    def rotate_image(self, angle):
        if self.current_image is None:
            return
        self.current_image = self.processor.rotate(self.current_image, angle)
        self.history.add_state(self.current_image.copy())
        self.display_image(self.current_image)
        
    def flip_image(self, direction):
        if self.current_image is None:
            return
        self.current_image = self.processor.flip(self.current_image, direction)
        self.history.add_state(self.current_image.copy())
        self.display_image(self.current_image)
        
    def crop_image(self):
        if self.current_image is None:
            QMessageBox.warning(self, "Error", "Open an image first")
            return
        dialog = CropDialog(self.current_image, self)
        if dialog.exec_():
            cropped = dialog.get_cropped_image()
            if cropped is not None:
                self.current_image = cropped
                self.history.add_state(cropped.copy())
                self.display_image(cropped)
                
    def resize_image(self):
        if self.current_image is None:
            QMessageBox.warning(self, "Error", "Open an image first")
            return
        dialog = ResizeDialog(self.current_image, self)
        if dialog.exec_():
            resized = dialog.get_resized_image()
            if resized is not None:
                self.current_image = resized
                self.history.add_state(resized.copy())
                self.display_image(resized)
                
    def show_histogram(self):
        if self.current_image is None:
            QMessageBox.warning(self, "Error", "Open an image first")
            return
        win = HistogramWindow(self.current_image, self)
        win.show()
        
    def open_batch_processing(self):
        from gui.batch_processing_dialog import BatchProcessingDialog
        dialog = BatchProcessingDialog(self.processor, self)
        dialog.exec_()
        
    def show_comparison(self):
        if self.current_image is None or self.original_image is None:
            QMessageBox.warning(self, "Error", "Open and edit an image first")
            return
        win = ComparisonWindow(self.original_image, self.current_image, self)
        win.show()
        
    def _on_zoom(self, level):
        self.zoom_level = level
        self.info_panel.update_zoom(level)
        if self.current_image is not None:
            self.display_image(self.current_image)
    
    def open_face_detection(self):
        if self.current_image is None:
            QMessageBox.warning(self, "خطا", "ابتدا یک تصویر باز کنید")
            return
        
        from gui.face_detection_dialog import FaceDetectionDialog
        dialog = FaceDetectionDialog(self.current_image, self.processor.face_detector, self)
        
        if dialog.exec_():
            result = dialog.get_processed_image()
            if result is not None:
                self.current_image = result
                self.history.add_state(result.copy())
                self.display_image(result)
    
    def open_blend_dialog(self):
        if self.current_image is None:
            QMessageBox.warning(self, "خطا", "ابتدا یک تصویر باز کنید")
            return
        
        from gui.image_blend_dialog import ImageBlendDialog
        dialog = ImageBlendDialog(self.current_image, self.processor, self)
        
        if dialog.exec_():
            result = dialog.get_result()
            if result is not None:
                self.current_image = result
                self.history.add_state(result.copy())
                self.display_image(result)
    
    def open_split_view(self):
        if self.current_image is None:
            QMessageBox.warning(self, "خطا", "ابتدا یک تصویر باز کنید")
            return
        
        from gui.split_view_dialog import SplitViewDialog
        dialog = SplitViewDialog(self.current_image, self)
        
        if dialog.exec_():
            result = dialog.get_result()
            if result is not None:
                self.current_image = result
                self.history.add_state(result.copy())
                self.display_image(result)
    
    def open_rotate_dialog(self):
        if self.current_image is None:
            QMessageBox.warning(self, "خطا", "ابتدا یک تصویر باز کنید")
            return
        
        from gui.rotate_dialog import RotateDialog
        dialog = RotateDialog(self.current_image, self.processor, self)
        
        if dialog.exec_():
            result = dialog.get_result()
            if result is not None:
                self.current_image = result
                self.history.add_state(result.copy())
                self.display_image(result)
    
    def open_shape_generator(self):
        from gui.shape_generator_dialog import ShapeGeneratorDialog
        dialog = ShapeGeneratorDialog(self)
        
        if dialog.exec_():
            result = dialog.get_result()
            if result is not None:
                self.current_image = result
                self.original_image = result.copy()
                self.history.clear()
                self.history.add_state(result.copy())
                self.display_image(result)
                self.info_panel.update_info(result)
    
    def open_video_processor(self):
        from gui.video_processor_dialog import VideoProcessorDialog
        dialog = VideoProcessorDialog(self.processor, self)
        dialog.exec_()

    # Alias for compatibility
    image_processor = property(lambda self: self.processor)
