"""
Drawing Tools - Line, rectangle, circle and text drawing
Copyright (c) 2024 D-speedster (github.com/D-speedster)
"""
import cv2


class DrawingTools:
    def __init__(self):
        self.active = False
        self.tool = None
        
    def draw_line(self, image, pt1, pt2, color=(0, 255, 0), thickness=2):
        cv2.line(image, pt1, pt2, color, thickness)
        return image
        
    def draw_rectangle(self, image, pt1, pt2, color=(0, 255, 0), thickness=2):
        cv2.rectangle(image, pt1, pt2, color, thickness)
        return image
        
    def draw_circle(self, image, center, radius, color=(0, 255, 0), thickness=2):
        cv2.circle(image, center, radius, color, thickness)
        return image
        
    def draw_text(self, image, text, pos, font_scale=1, color=(255, 255, 255), thickness=2):
        cv2.putText(image, text, pos, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
        return image
