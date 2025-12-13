"""
File Handler - Open and save image files
Copyright (c) 2024 D-speedster (github.com/D-speedster)
"""
import cv2
from PyQt5.QtWidgets import QFileDialog


class FileHandler:
    FORMATS = "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        
    def open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(None, "Open Image", "", self.FORMATS)
        return path
        
    def save_file_dialog(self):
        path, _ = QFileDialog.getSaveFileName(None, "Save Image", "", self.FORMATS)
        return path
        
    def load_image(self, path):
        try:
            return cv2.imread(path)
        except Exception:
            return None
            
    def save_image(self, image, path):
        try:
            cv2.imwrite(path, image)
            return True
        except Exception:
            return False
