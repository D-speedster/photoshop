"""
History - Undo/Redo functionality with temp file storage
Copyright (c) 2024 D-speedster (github.com/D-speedster)
"""
import cv2
import tempfile
import os
import shutil
import atexit


class History:
    def __init__(self, max_size=10):
        self.states = []
        self.current_index = -1
        self.max_size = max_size
        self.temp_dir = tempfile.mkdtemp(prefix="pe_hist_")
        atexit.register(self._cleanup_all)
        
    def add_state(self, image):
        self._remove_files(self.states[self.current_index + 1:])
        self.states = self.states[:self.current_index + 1]
        
        try:
            fd, path = tempfile.mkstemp(suffix='.png', dir=self.temp_dir)
            os.close(fd)
            cv2.imwrite(path, image)
            self.states.append(path)
            self.current_index += 1
            
            if len(self.states) > self.max_size:
                old = self.states.pop(0)
                self._remove_files([old])
                self.current_index -= 1
        except Exception:
            pass
            
    def undo(self):
        if self.current_index > 0:
            self.current_index -= 1
            return self._load(self.states[self.current_index])
        return None
        
    def redo(self):
        if self.current_index < len(self.states) - 1:
            self.current_index += 1
            return self._load(self.states[self.current_index])
        return None
        
    def clear(self):
        self._remove_files(self.states)
        self.states = []
        self.current_index = -1
        
    def _load(self, path):
        try:
            if os.path.exists(path):
                return cv2.imread(path)
        except Exception:
            pass
        return None
        
    def _remove_files(self, paths):
        for p in paths:
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass
                
    def _cleanup_all(self):
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass
            
    def __del__(self):
        self._cleanup_all()
