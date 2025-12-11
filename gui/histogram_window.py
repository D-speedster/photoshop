from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import cv2
import numpy as np


class HistogramWindow(QWidget):
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.image = image
        self.setWindowTitle("Histogram")
        self.setGeometry(300, 300, 800, 400)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        hist_img = self._create_histogram()
        
        label = QLabel()
        label.setAlignment(Qt.AlignCenter)
        
        h, w, ch = hist_img.shape
        qimg = QImage(hist_img.tobytes(), w, h, ch * w, QImage.Format_RGB888)
        label.setPixmap(QPixmap.fromImage(qimg))
        
        layout.addWidget(label)
        
    def _create_histogram(self):
        hist_w, hist_h = 768, 400
        hist_img = np.ones((hist_h, hist_w, 3), dtype=np.uint8) * 255
        
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        
        for i, color in enumerate(colors):
            hist = cv2.calcHist([self.image], [i], None, [256], [0, 256])
            cv2.normalize(hist, hist, 0, hist_h, cv2.NORM_MINMAX)
            
            bin_w = hist_w // 256
            for j in range(1, 256):
                cv2.line(hist_img,
                        (bin_w * (j-1), hist_h - int(hist[j-1])),
                        (bin_w * j, hist_h - int(hist[j])),
                        color, 2)
        
        return hist_img
