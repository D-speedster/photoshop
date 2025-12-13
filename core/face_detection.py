"""
Face Detection - Face, eyes and smile detection using Haar Cascades
Copyright (c) 2024 D-speedster (github.com/D-speedster)
"""
import cv2
import numpy as np
import os
import sys


def get_cascade_path():
    """Get path to haarcascades folder"""
    # First try cv2.data.haarcascades
    if hasattr(cv2, 'data') and cv2.data.haarcascades:
        return cv2.data.haarcascades
    
    # For PyInstaller bundled app
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        cascade_path = os.path.join(base_path, 'cv2', 'data')
        if os.path.exists(cascade_path):
            return cascade_path + os.sep
    
    # Fallback
    return cv2.data.haarcascades if hasattr(cv2, 'data') else ''


class FaceDetector:
    def __init__(self):
        cv2_path = get_cascade_path()
        
        self.face_cascade = self._load_cascade(cv2_path, 'haarcascade_frontalface_default.xml')
        self.face_cascade_alt = self._load_cascade(cv2_path, 'haarcascade_frontalface_alt2.xml')
        self.eye_cascade = self._load_cascade(cv2_path, 'haarcascade_eye.xml')
        self.eye_glasses = self._load_cascade(cv2_path, 'haarcascade_eye_tree_eyeglasses.xml')
        self.left_eye = self._load_cascade(cv2_path, 'haarcascade_lefteye_2splits.xml')
        self.right_eye = self._load_cascade(cv2_path, 'haarcascade_righteye_2splits.xml')
        self.smile_cascade = self._load_cascade(cv2_path, 'haarcascade_smile.xml')
        
    def _load_cascade(self, path, filename):
        """Load cascade with error handling"""
        full_path = os.path.join(path, filename) if path else filename
        cascade = cv2.CascadeClassifier(full_path)
        
        if cascade.empty():
            # Try alternative path
            alt_path = cv2.data.haarcascades + filename if hasattr(cv2, 'data') else filename
            cascade = cv2.CascadeClassifier(alt_path)
            
        return cascade
        
    def detect_faces_advanced(self, image, detect_eyes=True, detect_smile=False, min_size=50, accuracy=6):
        """تشخیص چهره با تنظیمات پیشرفته"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        
        result = image.copy()
        data = []
        
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=accuracy, minSize=(min_size, min_size)
        )
        
        for (x, y, w, h) in faces:
            face_data = {'rect': (x, y, w, h), 'eyes': [], 'smiles': []}
            cv2.rectangle(result, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            if detect_eyes:
                eyes = self._detect_eyes_improved(gray, (x, y, w, h))
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(result, (ex, ey), (ex+ew, ey+eh), (255, 0, 0), 2)
                    face_data['eyes'].append((ex, ey, ew, eh))
                    
            if detect_smile:
                roi = gray[y + int(h*0.5):y+h, x:x+w]
                smiles = self.smile_cascade.detectMultiScale(roi, 1.7, 22, minSize=(25, 25))
                for (sx, sy, sw, sh) in smiles:
                    real_y = y + int(h*0.5) + sy
                    cv2.rectangle(result, (x+sx, real_y), (x+sx+sw, real_y+sh), (0, 0, 255), 2)
                    face_data['smiles'].append((x+sx, real_y, sw, sh))
                    
            data.append(face_data)
            
        return result, data
        
    def _detect_eyes_improved(self, gray, face_rect):
        """تشخیص چشم با دقت بالا"""
        x, y, w, h = face_rect
        
        # ناحیه چشم‌ها (20% تا 55% از بالای صورت)
        eye_region_top = y + int(h * 0.15)
        eye_region_bottom = y + int(h * 0.55)
        roi = gray[eye_region_top:eye_region_bottom, x:x + w]
        
        # بهبود کنتراست ROI
        roi = cv2.equalizeHist(roi)
        
        # محاسبه اندازه مناسب چشم بر اساس اندازه صورت
        min_eye_w = int(w * 0.12)
        max_eye_w = int(w * 0.35)
        min_eye_h = int(h * 0.08)
        
        all_eyes = []
        
        # === روش 1: تقسیم صورت به دو نیمه و جستجوی جداگانه ===
        mid_x = w // 2
        
        # نیمه چپ صورت (چشم راست فرد)
        left_roi = roi[:, :mid_x + int(w * 0.1)]  # کمی overlap
        # نیمه راست صورت (چشم چپ فرد)
        right_roi = roi[:, mid_x - int(w * 0.1):]
        
        # تشخیص در نیمه چپ
        for cascade in [self.eye_cascade, self.eye_glasses, self.left_eye]:
            eyes = cascade.detectMultiScale(
                left_roi, 
                scaleFactor=1.05,  # دقیق‌تر
                minNeighbors=2,    # حساس‌تر
                minSize=(min_eye_w, min_eye_h),
                maxSize=(max_eye_w, int(h * 0.25))
            )
            for (ex, ey, ew, eh) in eyes:
                # فیلتر: چشم باید در محدوده منطقی باشه
                if ex < mid_x:
                    all_eyes.append([x + ex, eye_region_top + ey, ew, eh])
        
        # تشخیص در نیمه راست
        for cascade in [self.eye_cascade, self.eye_glasses, self.right_eye]:
            eyes = cascade.detectMultiScale(
                right_roi,
                scaleFactor=1.05,
                minNeighbors=2,
                minSize=(min_eye_w, min_eye_h),
                maxSize=(max_eye_w, int(h * 0.25))
            )
            for (ex, ey, ew, eh) in eyes:
                real_x = x + mid_x - int(w * 0.1) + ex
                # فیلتر: چشم باید در نیمه راست باشه
                if real_x > x + mid_x - int(w * 0.15):
                    all_eyes.append([real_x, eye_region_top + ey, ew, eh])
        
        # === روش 2: جستجوی کل ناحیه ===
        for cascade in [self.eye_cascade, self.eye_glasses]:
            eyes = cascade.detectMultiScale(
                roi,
                scaleFactor=1.08,
                minNeighbors=3,
                minSize=(min_eye_w, min_eye_h),
                maxSize=(max_eye_w, int(h * 0.25))
            )
            for (ex, ey, ew, eh) in eyes:
                all_eyes.append([x + ex, eye_region_top + ey, ew, eh])
        
        # حذف تکراری‌ها
        merged = self._merge_boxes(all_eyes, thresh=0.4)
        
        # انتخاب بهترین 2 چشم
        if len(merged) > 2:
            # مرتب‌سازی بر اساس موقعیت y (چشم‌ها باید تقریباً هم‌سطح باشن)
            merged = sorted(merged, key=lambda e: e[1])
            
            # انتخاب چشم‌هایی که در یک سطح هستن
            best_pair = self._select_best_eye_pair(merged, w)
            if best_pair:
                merged = best_pair
            else:
                merged = merged[:2]
            
        return merged
    
    def _select_best_eye_pair(self, eyes, face_width):
        """انتخاب بهترین جفت چشم"""
        if len(eyes) < 2:
            return eyes
            
        best_pair = None
        best_score = float('inf')
        
        for i in range(len(eyes)):
            for j in range(i + 1, len(eyes)):
                e1, e2 = eyes[i], eyes[j]
                
                # فاصله افقی بین دو چشم
                dist_x = abs((e1[0] + e1[2]/2) - (e2[0] + e2[2]/2))
                
                # اختلاف ارتفاع (باید کم باشه)
                dist_y = abs((e1[1] + e1[3]/2) - (e2[1] + e2[3]/2))
                
                # فاصله افقی باید بین 25% تا 70% عرض صورت باشه
                if face_width * 0.25 < dist_x < face_width * 0.70:
                    # اختلاف ارتفاع باید کم باشه
                    if dist_y < face_width * 0.15:
                        score = dist_y + abs(dist_x - face_width * 0.4)
                        if score < best_score:
                            best_score = score
                            best_pair = [e1, e2]
        
        return best_pair
        
    def _merge_boxes(self, boxes, thresh=0.3):
        """ادغام باکس‌های همپوشان"""
        if len(boxes) == 0:
            return []
            
        boxes = np.array(boxes)
        x1, y1 = boxes[:, 0], boxes[:, 1]
        x2, y2 = boxes[:, 0] + boxes[:, 2], boxes[:, 1] + boxes[:, 3]
        areas = boxes[:, 2] * boxes[:, 3]
        
        indices = np.argsort(areas)[::-1]
        keep = []
        
        while len(indices) > 0:
            i = indices[0]
            keep.append(i)
            
            if len(indices) == 1:
                break
                
            xx1 = np.maximum(x1[i], x1[indices[1:]])
            yy1 = np.maximum(y1[i], y1[indices[1:]])
            xx2 = np.minimum(x2[i], x2[indices[1:]])
            yy2 = np.minimum(y2[i], y2[indices[1:]])
            
            w = np.maximum(0, xx2 - xx1)
            h = np.maximum(0, yy2 - yy1)
            
            overlap = (w * h) / areas[indices[1:]]
            indices = indices[1:][overlap < thresh]
            
        return boxes[keep].tolist()
        
    def blur_faces_advanced(self, image, min_size=50, accuracy=6):
        """محو کردن چهره‌ها"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        result = image.copy()
        
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=accuracy, minSize=(min_size, min_size)
        )
        
        for (x, y, w, h) in faces:
            roi = result[y:y+h, x:x+w]
            blurred = cv2.GaussianBlur(roi, (99, 99), 30)
            result[y:y+h, x:x+w] = blurred
            
        return result
        
    def pixelate_faces_advanced(self, image, pixel_size=15, min_size=50, accuracy=6):
        """پیکسلی کردن چهره‌ها"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        result = image.copy()
        
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=accuracy, minSize=(min_size, min_size)
        )
        
        for (x, y, w, h) in faces:
            roi = result[y:y+h, x:x+w]
            small = cv2.resize(roi, (pixel_size, pixel_size), interpolation=cv2.INTER_LINEAR)
            pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
            result[y:y+h, x:x+w] = pixelated
            
        return result
        
    def add_emoji_advanced(self, image, emoji_type='sunglasses', min_size=50, accuracy=6):
        """اضافه کردن ایموجی"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        result = image.copy()
        
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=accuracy, minSize=(min_size, min_size)
        )
        
        for (x, y, w, h) in faces:
            if emoji_type == 'sunglasses':
                # رسم عینک ساده
                eye_y = y + int(h * 0.35)
                cv2.rectangle(result, (x + int(w*0.1), eye_y), (x + int(w*0.4), eye_y + int(h*0.15)), (0, 0, 0), -1)
                cv2.rectangle(result, (x + int(w*0.6), eye_y), (x + int(w*0.9), eye_y + int(h*0.15)), (0, 0, 0), -1)
                cv2.line(result, (x + int(w*0.4), eye_y + int(h*0.07)), (x + int(w*0.6), eye_y + int(h*0.07)), (0, 0, 0), 3)
            elif emoji_type == 'mask':
                # رسم ماسک ساده
                mask_y = y + int(h * 0.5)
                pts = np.array([
                    [x + int(w*0.1), mask_y],
                    [x + int(w*0.9), mask_y],
                    [x + int(w*0.85), y + h],
                    [x + int(w*0.15), y + h]
                ], np.int32)
                cv2.fillPoly(result, [pts], (200, 200, 200))
                cv2.polylines(result, [pts], True, (150, 150, 150), 2)
                
        return result
        
    def count_faces_advanced(self, image, min_size=50, accuracy=6):
        """شمارش چهره‌ها"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=accuracy, minSize=(min_size, min_size)
        )
        
        return len(faces)
