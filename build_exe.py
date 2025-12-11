import PyInstaller.__main__
import os
import cv2

base_dir = os.path.dirname(os.path.abspath(__file__))

# پیدا کردن مسیر فایل‌های cascade
haarcascades_path = cv2.data.haarcascades
print(f"Haarcascades path: {haarcascades_path}")

build_args = [
    'main.py',
    '--name=PhotoEditor',
    '--onefile',
    '--windowed',
    f'--add-data=assets;assets',
    f'--add-data={haarcascades_path};cv2/data',
    '--hidden-import=PyQt5',
    '--hidden-import=PyQt5.QtWidgets',
    '--hidden-import=PyQt5.QtCore',
    '--hidden-import=PyQt5.QtGui',
    '--hidden-import=cv2',
    '--hidden-import=numpy',
    '--hidden-import=PIL',
    '--hidden-import=PIL.Image',
    '--hidden-import=PIL.ImageDraw',
    '--hidden-import=PIL.ImageFont',
    '--collect-all=cv2',
    '--clean',
]

# اضافه کردن آیکون اگر وجود داره
icon_path = os.path.join(base_dir, 'assets', 'icons', 'app_icon.ico')
if os.path.exists(icon_path):
    build_args.insert(4, f'--icon={icon_path}')

print("Building PhotoEditor...")
print("This may take a few minutes...")

PyInstaller.__main__.run(build_args)

print("\n" + "="*50)
print("Build completed successfully!")
print("Output file: dist/PhotoEditor.exe")
print("="*50)
