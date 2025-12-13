"""
Webcam - Camera capture functionality
Copyright (c) 2024 D-speedster (github.com/D-speedster)
"""
import cv2


class Webcam:
    def __init__(self):
        self.camera = None
        self.is_running = False
        self.last_error = None
        
    def start(self, camera_index=0):
        try:
            self.camera = cv2.VideoCapture(camera_index)
            if self.camera.isOpened():
                self.is_running = True
                self.last_error = None
                return True
            self.last_error = "Could not open camera"
        except Exception as e:
            self.last_error = str(e)
        return False
        
    def stop(self):
        if self.camera is not None:
            try:
                self.camera.release()
            except Exception:
                pass
            self.is_running = False
            
    def get_frame(self):
        if self.camera is None or not self.is_running:
            return None
            
        try:
            ret, frame = self.camera.read()
            if ret:
                return frame
            self.last_error = "Failed to read frame"
        except Exception as e:
            self.last_error = str(e)
            self.is_running = False
        return None
        
    def get_error(self):
        return self.last_error
        
    def __del__(self):
        self.stop()
