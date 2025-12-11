import os
import sys
import cv2


def get_base_path():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def get_haarcascades_path():
    """پیدا کردن مسیر فایل‌های cascade"""
    # اول در مسیر exe چک کن
    if hasattr(sys, '_MEIPASS'):
        exe_path = os.path.join(sys._MEIPASS, 'cv2', 'data')
        if os.path.exists(exe_path):
            return exe_path
    
    # بعد مسیر پیش‌فرض cv2
    return cv2.data.haarcascades


BASE_PATH = get_base_path()
ASSETS_PATH = os.path.join(BASE_PATH, 'assets')
STYLES_PATH = os.path.join(ASSETS_PATH, 'styles_modern.css')

HAARCASCADES_PATH = get_haarcascades_path()
FACE_CASCADE_PATH = os.path.join(HAARCASCADES_PATH, 'haarcascade_frontalface_default.xml')
EYE_CASCADE_PATH = os.path.join(HAARCASCADES_PATH, 'haarcascade_eye.xml')
SMILE_CASCADE_PATH = os.path.join(HAARCASCADES_PATH, 'haarcascade_smile.xml')
