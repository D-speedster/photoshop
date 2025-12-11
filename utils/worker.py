from PyQt5.QtCore import QThread, pyqtSignal
import traceback
import sys


class Worker(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(tuple)
    progress = pyqtSignal(int)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception:
            exc_type, exc_val = sys.exc_info()[:2]
            self.error.emit((exc_type, exc_val, traceback.format_exc()))
