"""
Build executable using PyInstaller
Copyright (c) 2024 D-speedster (github.com/D-speedster)
"""
import PyInstaller.__main__
import cv2
import os

# Get OpenCV data path for haarcascades
cv2_data_path = os.path.dirname(cv2.data.haarcascades)

PyInstaller.__main__.run([
    'main.py',
    '--name=PhotoEditor',
    '--onefile',
    '--windowed',
    '--add-data=assets;assets',
    f'--add-data={cv2_data_path};cv2/data',
    '--hidden-import=PyQt5',
    '--hidden-import=cv2',
    '--hidden-import=numpy',
    '--hidden-import=PIL',
    '--hidden-import=arabic_reshaper',
    '--hidden-import=bidi',
    '--clean',
])

print("\nBuild complete! Check the 'dist' folder.")
