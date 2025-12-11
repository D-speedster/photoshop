from PyQt5.QtWidgets import QLabel, QColorDialog, QInputDialog
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QPixmap, QImage
import cv2
import numpy as np


class DrawingCanvas(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.drawing = False
        self.current_tool = None
        self.start_point = None
        self.end_point = None
        self.temp_pixmap = None
        self.draw_color = (0, 255, 0)
        self.line_thickness = 3
        self.active_mode = None
        self.selection_tool = None
        self.color_picker = None
        
    def set_tool(self, tool_name):
        self.current_tool = tool_name
        self.shape_settings = None
        self.text_settings = None
        self.polygon_points = []
        
        if tool_name in ["line", "rectangle", "circle", "ellipse", "polygon"]:
            from gui.shape_settings_dialog import ShapeSettingsDialog
            dialog = ShapeSettingsDialog(tool_name, self)
            if dialog.exec_():
                self.shape_settings = dialog.get_settings()
                self.setCursor(Qt.CrossCursor)
            else:
                self.current_tool = None
                return
        elif tool_name == "text":
            from gui.advanced_text_dialog import AdvancedTextDialog
            dialog = AdvancedTextDialog(self)
            if dialog.exec_():
                self.text_settings = dialog.get_settings()
                self.setCursor(Qt.CrossCursor)
            else:
                self.current_tool = None
                return
        
        if tool_name:
            self.setCursor(Qt.CrossCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
            
    def set_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.draw_color = (color.blue(), color.green(), color.red())
            
    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
            
        if self.active_mode == 'selection' and self.selection_tool:
            # ذخیره pixmap برای پیش‌نمایش
            if self.pixmap():
                self.temp_pixmap = self.pixmap().copy()
            self.selection_tool.handle_mouse_press(event.pos())
            return
            
        if self.active_mode == 'colorpicker' and self.color_picker:
            self.color_picker.handle_pick(event.pos())
            return
            
        if self.current_tool:
            self.drawing = True
            self.start_point = event.pos()
            self.temp_pixmap = self.pixmap().copy() if self.pixmap() else None
            
    def mouseMoveEvent(self, event):
        if self.active_mode == 'selection' and self.selection_tool:
            self.selection_tool.handle_mouse_move(event.pos())
            # نمایش کادر انتخاب در حین کشیدن
            if self.selection_tool.state.selecting and self.temp_pixmap:
                self._draw_selection_preview(event.pos())
            return
            
        if self.drawing and self.temp_pixmap:
            self.end_point = event.pos()
            preview_pixmap = self.temp_pixmap.copy()
            painter = QPainter(preview_pixmap)
            pen = QPen(Qt.green, self.line_thickness)
            painter.setPen(pen)
            
            if self.current_tool == "line":
                painter.drawLine(self.start_point, self.end_point)
            elif self.current_tool == "rectangle":
                painter.drawRect(self.start_point.x(), self.start_point.y(),
                               self.end_point.x() - self.start_point.x(),
                               self.end_point.y() - self.start_point.y())
            elif self.current_tool == "circle":
                radius = int(((self.end_point.x() - self.start_point.x())**2 + 
                            (self.end_point.y() - self.start_point.y())**2)**0.5)
                painter.drawEllipse(self.start_point, radius, radius)
            elif self.current_tool == "ellipse":
                w = abs(self.end_point.x() - self.start_point.x())
                h = abs(self.end_point.y() - self.start_point.y())
                x = min(self.start_point.x(), self.end_point.x())
                y = min(self.start_point.y(), self.end_point.y())
                painter.drawEllipse(x, y, w, h)
                
            painter.end()
            self.setPixmap(preview_pixmap)
            
    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
            
        if self.active_mode == 'selection' and self.selection_tool:
            self.selection_tool.handle_mouse_release(event.pos())
            # برگرداندن تصویر اصلی و نمایش کادر نهایی
            if self.temp_pixmap:
                self._draw_final_selection()
            self.temp_pixmap = None
            return
            
        if self.drawing:
            self.drawing = False
            self.end_point = event.pos()
            
            if self.parent_window and self.parent_window.current_image is not None:
                self.draw_on_image()
                
            self.start_point = None
            self.end_point = None
            self.temp_pixmap = None
            
    def draw_on_image(self):
        if not self.start_point or not self.end_point:
            return
            
        image = self.parent_window.current_image.copy()
        label_size = self.size()
        img_h, img_w = image.shape[:2]
        
        scale_w = img_w / label_size.width()
        scale_h = img_h / label_size.height()
        scale = max(scale_w, scale_h)
        
        x1 = int(self.start_point.x() * scale)
        y1 = int(self.start_point.y() * scale)
        x2 = int(self.end_point.x() * scale)
        y2 = int(self.end_point.y() * scale)
        
        if self.current_tool == "line" and self.shape_settings:
            color = self.shape_settings['line_color']
            thickness = self.shape_settings['thickness']
            cv2.line(image, (x1, y1), (x2, y2), color, thickness)
            
        elif self.current_tool == "rectangle" and self.shape_settings:
            color = self.shape_settings['line_color']
            thickness = self.shape_settings['thickness']
            
            if self.shape_settings['fill']:
                cv2.rectangle(image, (x1, y1), (x2, y2), self.shape_settings['fill_color'], -1)
            cv2.rectangle(image, (x1, y1), (x2, y2), color, max(1, thickness))
            
        elif self.current_tool == "circle" and self.shape_settings:
            radius = int(((x2 - x1)**2 + (y2 - y1)**2)**0.5)
            color = self.shape_settings['line_color']
            thickness = self.shape_settings['thickness']
            
            if self.shape_settings['fill']:
                cv2.circle(image, (x1, y1), radius, self.shape_settings['fill_color'], -1)
            cv2.circle(image, (x1, y1), radius, color, max(1, thickness))
            
        elif self.current_tool == "ellipse" and self.shape_settings:
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            ax = abs(x2 - x1) // 2
            ay = abs(y2 - y1) // 2
            color = self.shape_settings['line_color']
            thickness = self.shape_settings['thickness']
            
            if self.shape_settings['fill']:
                cv2.ellipse(image, (cx, cy), (ax, ay), 0, 0, 360, self.shape_settings['fill_color'], -1)
            cv2.ellipse(image, (cx, cy), (ax, ay), 0, 0, 360, color, max(1, thickness))
            
        elif self.current_tool == "text" and self.text_settings:
            text = self.text_settings['text']
            if text:
                if self.text_settings.get('is_persian', False):
                    image = self._draw_persian_text(image, text, x1, y1)
                else:
                    image = self._draw_english_text(image, text, x1, y1)
        
        self.parent_window.current_image = image
        self.parent_window.history.add_state(image.copy())
        self.parent_window.display_image(image)
        self.set_tool(None)
        
    def _draw_persian_text(self, image, text, x, y):
        from PIL import Image as PILImage, ImageDraw, ImageFont
        try:
            from arabic_reshaper import reshape
            from bidi.algorithm import get_display
            
            reshaped = reshape(text)
            bidi_text = get_display(reshaped)
            
            pil_img = PILImage.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_img)
            
            font_size = int(self.text_settings['scale'] * 40)
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/tahoma.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            b, g, r = self.text_settings['color']
            rgb_color = (r, g, b)
            
            if self.text_settings['has_background'] and self.text_settings['bg_color']:
                bbox = draw.textbbox((x, y), bidi_text, font=font)
                bg_b, bg_g, bg_r = self.text_settings['bg_color']
                draw.rectangle(bbox, fill=(bg_r, bg_g, bg_b))
            
            draw.text((x, y), bidi_text, font=font, fill=rgb_color)
            return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            
        except Exception:
            return self._draw_english_text(image, text, x, y)
            
    def _draw_english_text(self, image, text, x, y):
        font = self.text_settings['font']
        scale = self.text_settings['scale']
        color = self.text_settings['color']
        thickness = self.text_settings['thickness']
        
        if self.text_settings['has_background'] and self.text_settings['bg_color']:
            (tw, th), baseline = cv2.getTextSize(text, font, scale, thickness)
            cv2.rectangle(image, (x - 5, y - th - 5), (x + tw + 5, y + baseline + 5),
                         self.text_settings['bg_color'], -1)
        
        cv2.putText(image, text, (x, y), font, scale, color, thickness)
        return image
    
    def _draw_selection_preview(self, current_pos):
        """نمایش کادر انتخاب در حین کشیدن"""
        if not self.temp_pixmap or not self.selection_tool:
            return
            
        start = self.selection_tool.state.start
        if not start:
            return
            
        preview = self.temp_pixmap.copy()
        painter = QPainter(preview)
        
        # کادر با خط‌چین آبی
        pen = QPen(Qt.cyan, 2, Qt.DashLine)
        painter.setPen(pen)
        
        x1, y1 = start.x(), start.y()
        x2, y2 = current_pos.x(), current_pos.y()
        
        # رسم مستطیل
        painter.drawRect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        
        # نمایش اندازه
        w, h = abs(x2 - x1), abs(y2 - y1)
        painter.setPen(QPen(Qt.white))
        painter.drawText(min(x1, x2) + 5, min(y1, y2) - 5, f"{w} × {h}")
        
        painter.end()
        self.setPixmap(preview)
    
    def _draw_final_selection(self):
        """نمایش کادر انتخاب نهایی"""
        if not self.selection_tool or not self.selection_tool.state.rect:
            if self.temp_pixmap:
                self.setPixmap(self.temp_pixmap)
            return
            
        rect = self.selection_tool.state.rect
        preview = self.temp_pixmap.copy()
        painter = QPainter(preview)
        
        # کادر نهایی با خط ثابت
        pen = QPen(Qt.cyan, 2, Qt.SolidLine)
        painter.setPen(pen)
        painter.drawRect(rect)
        
        # گوشه‌های کادر (handles)
        handle_size = 6
        painter.setBrush(Qt.cyan)
        corners = [
            (rect.x(), rect.y()),
            (rect.x() + rect.width(), rect.y()),
            (rect.x(), rect.y() + rect.height()),
            (rect.x() + rect.width(), rect.y() + rect.height())
        ]
        for cx, cy in corners:
            painter.drawRect(cx - handle_size//2, cy - handle_size//2, handle_size, handle_size)
        
        painter.end()
        self.setPixmap(preview)
