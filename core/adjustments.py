"""
Image Adjustments - Brightness, Contrast, Saturation
Copyright (c) 2024 D-speedster (github.com/D-speedster)
"""
import cv2
import numpy as np


class Adjustments:
    def brightness(self, image, value):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] + value, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
    def contrast(self, image, value):
        value = np.clip(value, -255, 254)
        factor = (259 * (value + 255)) / (255 * (259 - value))
        result = factor * (image.astype(np.float32) - 128) + 128
        return np.clip(result, 0, 255).astype(np.uint8)
        
    def saturation(self, image, value):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] + value, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
