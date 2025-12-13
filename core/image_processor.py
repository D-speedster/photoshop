"""
Image Processor - Main image processing engine
Copyright (c) 2024 D-speedster (github.com/D-speedster)
"""
import cv2
import numpy as np
from core.filters import Filters
from core.adjustments import Adjustments
from core.drawing_tools import DrawingTools
from core.face_detection import FaceDetector


class ImageProcessor:
    def __init__(self):
        self.filters = Filters()
        self.adjustments = Adjustments()
        self.drawing_tools = DrawingTools()
        self.face_detector = FaceDetector()
        
    def apply_filter(self, image, filter_name, **params):
        if image is None:
            return None
            
        methods = {
            'blur': self.filters.blur,
            'sharpen': self.filters.sharpen,
            'edge': self.filters.edge_detection,
            'emboss': self.filters.emboss,
            'grayscale': self.filters.grayscale,
            'sepia': self.filters.sepia,
            'invert': self.filters.invert,
            'cartoon': self.filters.cartoon,
            'median': self.filters.median,
            'remove_red': lambda img: self.filters.remove_channel(img, 'red'),
            'remove_green': lambda img: self.filters.remove_channel(img, 'green'),
            'remove_blue': lambda img: self.filters.remove_channel(img, 'blue'),
            'only_red': lambda img: self.filters.keep_channel(img, 'red'),
            'only_green': lambda img: self.filters.keep_channel(img, 'green'),
            'only_blue': lambda img: self.filters.keep_channel(img, 'blue'),
            'corners': self.filters.corner_detection,
            'harris': self.filters.harris_corners,
        }
        
        if filter_name in methods:
            return methods[filter_name](image, **params)
        return image
        
    def apply_adjustment(self, image, adj_type, value):
        if image is None:
            return None
            
        methods = {
            'brightness': self.adjustments.brightness,
            'contrast': self.adjustments.contrast,
            'saturation': self.adjustments.saturation
        }
        
        if adj_type in methods:
            return methods[adj_type](image, value)
        return image
        
    def rotate(self, image, angle):
        if angle == 90:
            return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == -90:
            return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif angle == 180:
            return cv2.rotate(image, cv2.ROTATE_180)
        return image
    
    def rotate_free(self, image, angle):
        h, w = image.shape[:2]
        cx, cy = w // 2, h // 2
        matrix = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
        
        cos = np.abs(matrix[0, 0])
        sin = np.abs(matrix[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        
        matrix[0, 2] += (new_w / 2) - cx
        matrix[1, 2] += (new_h / 2) - cy
        
        return cv2.warpAffine(image, matrix, (new_w, new_h), borderValue=(255, 255, 255))
        
    def flip(self, image, direction):
        if direction == "horizontal":
            return cv2.flip(image, 1)
        elif direction == "vertical":
            return cv2.flip(image, 0)
        return image
        
    def crop(self, image, x, y, w, h):
        return image[y:y+h, x:x+w]
        
    def resize(self, image, width, height):
        h, w = image.shape[:2]
        interp = cv2.INTER_CUBIC if width > w or height > h else cv2.INTER_AREA
        return cv2.resize(image, (width, height), interpolation=interp)
        
    def add_text(self, image, text, position, color=(255, 255, 255)):
        result = image.copy()
        return self.drawing_tools.draw_text(result, text, position, color=color)
        
    def calculate_histogram(self, image):
        histograms = []
        for i in range(3):
            hist = cv2.calcHist([image], [i], None, [256], [0, 256])
            histograms.append(hist)
        return histograms
    
    def bitwise_and(self, img1, img2):
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        return cv2.bitwise_and(img1, img2)
    
    def bitwise_or(self, img1, img2):
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        return cv2.bitwise_or(img1, img2)
    
    def bitwise_xor(self, img1, img2):
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        return cv2.bitwise_xor(img1, img2)
    
    def add_images(self, img1, img2):
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        return cv2.add(img1, img2)
    
    def blend_images(self, img1, img2, alpha=0.5):
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        beta = 1.0 - alpha
        return cv2.addWeighted(img1, alpha, img2, beta, 0)
    
    def side_by_side(self, img1, img2):
        gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        if img1.shape[0] != gray_bgr.shape[0]:
            gray_bgr = cv2.resize(gray_bgr, (img1.shape[1], img1.shape[0]))
        return np.hstack([img1, gray_bgr])
    
    def split_view(self, image, position=50):
        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        split_x = int(w * position / 100)
        result = image.copy()
        result[:, split_x:] = gray_bgr[:, split_x:]
        cv2.line(result, (split_x, 0), (split_x, h), (0, 255, 0), 2)
        return result
