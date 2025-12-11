import cv2
import numpy as np
from utils.constants import FACE_CASCADE_PATH, EYE_CASCADE_PATH, SMILE_CASCADE_PATH


class FaceDetection:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)
        self.eye_cascade = cv2.CascadeClassifier(EYE_CASCADE_PATH)
        self.smile_cascade = cv2.CascadeClassifier(SMILE_CASCADE_PATH)
        
        # کسکید اضافی برای چشم با عینک
        eye_glasses_path = cv2.data.haarcascades + 'haarcascade_eye_tree_eyeglasses.xml'
        self.eye_glasses_cascade = cv2.CascadeClassifier(eye_glasses_path)
        
    def _detect_faces_base(self, image, min_size=50, neighbors=6):
        """تشخیص پایه چهره"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=neighbors, 
            minSize=(min_size, min_size),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        return faces, gray
    
    def _detect_eyes_in_face(self, gray_face, face_w, face_h):
        """تشخیص چشم در ناحیه چهره"""
        # ناحیه چشم: 15% تا 50% ارتفاع چهره
        y1, y2 = int(face_h * 0.15), int(face_h * 0.55)
        upper_face = gray_face[y1:y2, :]
        
        all_eyes = []
        
        # تلاش با هر دو کسکید
        for cascade in [self.eye_cascade, self.eye_glasses_cascade]:
            eyes = cascade.detectMultiScale(
                upper_face,
                scaleFactor=1.05,
                minNeighbors=2,
                minSize=(int(face_w * 0.08), int(face_w * 0.08)),
                maxSize=(int(face_w * 0.35), int(face_w * 0.35))
            )
            for e in eyes:
                all_eyes.append(e)
        
        # فیلتر چشم‌ها
        left_eyes = []
        right_eyes = []
        
        for (ex, ey, ew, eh) in all_eyes:
            center_x = ex + ew // 2
            
            # چشم چپ (در نیمه راست تصویر چون آینه‌ای)
            if center_x < face_w * 0.45:
                left_eyes.append((ex, ey + y1, ew, eh, ew * eh))  # اضافه کردن مساحت
            # چشم راست
            elif center_x > face_w * 0.55:
                right_eyes.append((ex, ey + y1, ew, eh, ew * eh))
        
        result = []
        
        # انتخاب بزرگترین چشم از هر طرف
        if left_eyes:
            left_eyes.sort(key=lambda e: e[4], reverse=True)
            best = left_eyes[0]
            result.append((best[0], best[1], best[2], best[3]))
        
        if right_eyes:
            right_eyes.sort(key=lambda e: e[4], reverse=True)
            best = right_eyes[0]
            result.append((best[0], best[1], best[2], best[3]))
        
        return result
    
    def _detect_smile_in_face(self, gray_face, face_w, face_h):
        """تشخیص لبخند در ناحیه چهره"""
        # فقط نیمه پایین چهره
        lower_face = gray_face[int(face_h * 0.5):, :]
        
        smiles = self.smile_cascade.detectMultiScale(
            lower_face,
            scaleFactor=1.2,
            minNeighbors=8,
            minSize=(int(face_w * 0.2), int(face_w * 0.05)),
            maxSize=(int(face_w * 0.8), int(face_w * 0.4))
        )
        
        # فیلتر لبخندهای معتبر
        valid_smiles = []
        for (sx, sy, sw, sh) in smiles:
            center_x = sx + sw // 2
            # لبخند باید وسط چهره باشه
            if face_w * 0.2 < center_x < face_w * 0.8:
                valid_smiles.append((sx, sy, sw, sh))
        
        return valid_smiles[:1]  # فقط 1 لبخند
        
    def detect_faces(self, image, detect_eyes=False, detect_smile=False):
        return self.detect_faces_advanced(image, detect_eyes, detect_smile, 50, 6)
    
    def detect_faces_advanced(self, image, detect_eyes=False, detect_smile=False, 
                              min_size=50, neighbors=6):
        if image is None:
            return None, []
            
        result = image.copy()
        faces, gray = self._detect_faces_base(image, min_size, neighbors)
        face_data = []
        
        for i, (x, y, w, h) in enumerate(faces):
            cv2.rectangle(result, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(result, f'{i+1}', (x+5, y+20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            info = {'position': (x, y, w, h), 'eyes': [], 'smiles': []}
            
            # استخراج ناحیه چهره
            face_gray = gray[y:y+h, x:x+w]
            face_color = result[y:y+h, x:x+w]
            
            if detect_eyes:
                eyes = self._detect_eyes_in_face(face_gray, w, h)
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(face_color, (ex, ey), (ex+ew, ey+eh), (255, 0, 0), 2)
                    info['eyes'].append((ex, ey, ew, eh))
            
            if detect_smile:
                smiles = self._detect_smile_in_face(face_gray, w, h)
                for (sx, sy, sw, sh) in smiles:
                    # تنظیم موقعیت y برای نیمه پایین
                    actual_sy = sy + int(h * 0.5)
                    cv2.rectangle(face_color, (sx, actual_sy), (sx+sw, actual_sy+sh), (0, 0, 255), 2)
                    info['smiles'].append((sx, actual_sy, sw, sh))
            
            face_data.append(info)
        
        return result, face_data
    
    def blur_faces(self, image):
        return self.blur_faces_advanced(image, 50, 6)
    
    def blur_faces_advanced(self, image, min_size=50, neighbors=6):
        if image is None:
            return None
        result = image.copy()
        faces, _ = self._detect_faces_base(image, min_size, neighbors)
        for (x, y, w, h) in faces:
            face = result[y:y+h, x:x+w]
            blur_amount = max(99, w // 2 * 2 + 1)
            result[y:y+h, x:x+w] = cv2.GaussianBlur(face, (blur_amount, blur_amount), 30)
        return result
    
    def pixelate_faces(self, image, pixel_size=20):
        return self.pixelate_faces_advanced(image, pixel_size, 50, 6)
    
    def pixelate_faces_advanced(self, image, pixel_size=15, min_size=50, neighbors=6):
        if image is None:
            return None
        result = image.copy()
        faces, _ = self._detect_faces_base(image, min_size, neighbors)
        for (x, y, w, h) in faces:
            face = result[y:y+h, x:x+w]
            px = max(pixel_size, w // 10)
            small = cv2.resize(face, (px, px), interpolation=cv2.INTER_LINEAR)
            result[y:y+h, x:x+w] = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        return result
    
    def add_emoji_to_faces(self, image, emoji_type='sunglasses'):
        return self.add_emoji_advanced(image, emoji_type, 50, 6)
    
    def add_emoji_advanced(self, image, emoji_type='sunglasses', min_size=50, neighbors=6):
        if image is None:
            return None
        result = image.copy()
        faces, _ = self._detect_faces_base(image, min_size, neighbors)
        
        for (x, y, w, h) in faces:
            if emoji_type == 'sunglasses':
                ey = y + int(h * 0.28)
                eh = int(h * 0.18)
                ex = x + int(w * 0.05)
                ew = int(w * 0.9)
                glass_w = int(ew * 0.4)
                
                cv2.ellipse(result, (ex + glass_w//2, ey + eh//2), 
                           (glass_w//2, eh//2), 0, 0, 360, (20, 20, 20), -1)
                cv2.ellipse(result, (ex + glass_w//2, ey + eh//2), 
                           (glass_w//2, eh//2), 0, 0, 360, (60, 60, 60), 2)
                cv2.ellipse(result, (ex + ew - glass_w//2, ey + eh//2), 
                           (glass_w//2, eh//2), 0, 0, 360, (20, 20, 20), -1)
                cv2.ellipse(result, (ex + ew - glass_w//2, ey + eh//2), 
                           (glass_w//2, eh//2), 0, 0, 360, (60, 60, 60), 2)
                cv2.line(result, (ex + glass_w, ey + eh//2), 
                        (ex + ew - glass_w, ey + eh//2), (60, 60, 60), 3)
                
            elif emoji_type == 'mask':
                my = y + int(h * 0.45)
                mh = int(h * 0.45)
                mx = x + int(w * 0.05)
                mw = int(w * 0.9)
                pts = np.array([
                    [mx, my + mh//4], [mx + mw//4, my], [mx + mw*3//4, my],
                    [mx + mw, my + mh//4], [mx + mw, my + mh*3//4],
                    [mx + mw//2, my + mh], [mx, my + mh*3//4]
                ], np.int32)
                cv2.fillPoly(result, [pts], (220, 220, 220))
                cv2.polylines(result, [pts], True, (180, 180, 180), 2)
        return result
    
    def count_faces(self, image):
        return self.count_faces_advanced(image, 50, 6)
    
    def count_faces_advanced(self, image, min_size=50, neighbors=6):
        if image is None:
            return 0
        faces, _ = self._detect_faces_base(image, min_size, neighbors)
        return len(faces)
