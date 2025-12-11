import cv2
import numpy as np


class Filters:
    def blur(self, image, kernel_size=15):
        k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
        return cv2.GaussianBlur(image, (k, k), 0)
        
    def sharpen(self, image):
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        return cv2.filter2D(image, -1, kernel)
        
    def edge_detection(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
    def emboss(self, image):
        kernel = np.array([[-2, -1, 0],
                          [-1,  1, 1],
                          [ 0,  1, 2]])
        return cv2.filter2D(image, -1, kernel)
        
    def grayscale(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
    def sepia(self, image):
        kernel = np.array([[0.272, 0.534, 0.131],
                          [0.349, 0.686, 0.168],
                          [0.393, 0.769, 0.189]])
        result = cv2.transform(image, kernel)
        return np.clip(result, 0, 255).astype(np.uint8)
        
    def invert(self, image):
        return cv2.bitwise_not(image)
        
    def cartoon(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                     cv2.THRESH_BINARY, 9, 9)
        color = cv2.bilateralFilter(image, 9, 300, 300)
        return cv2.bitwise_and(color, color, mask=edges)
    
    def median(self, image, kernel_size=5):
        k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
        return cv2.medianBlur(image, k)
    
    def remove_channel(self, image, channel='red'):
        result = image.copy()
        if channel == 'red':
            result[:, :, 2] = 0
        elif channel == 'green':
            result[:, :, 1] = 0
        elif channel == 'blue':
            result[:, :, 0] = 0
        return result
    
    def keep_channel(self, image, channel='red'):
        result = np.zeros_like(image)
        if channel == 'red':
            result[:, :, 2] = image[:, :, 2]
        elif channel == 'green':
            result[:, :, 1] = image[:, :, 1]
        elif channel == 'blue':
            result[:, :, 0] = image[:, :, 0]
        return result
    
    def corner_detection(self, image, max_corners=100, quality=0.01, min_distance=10):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        corners = cv2.goodFeaturesToTrack(gray, max_corners, quality, min_distance)
        result = image.copy()
        if corners is not None:
            for corner in corners:
                x, y = corner.ravel()
                cv2.circle(result, (int(x), int(y)), 5, (0, 255, 0), -1)
        return result
    
    def harris_corners(self, image, block_size=2, ksize=3, k=0.04):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = np.float32(gray)
        dst = cv2.cornerHarris(gray, block_size, ksize, k)
        dst = cv2.dilate(dst, None)
        result = image.copy()
        result[dst > 0.01 * dst.max()] = [0, 0, 255]
        return result
