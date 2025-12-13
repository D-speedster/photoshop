"""
Build executable using PyInstaller
Copyright (c) 2024 D-speedster (github.com/D-speedster)
"""
import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--name=PhotoEditor',
    '--onefile',
    '--windowed',
    '--add-data=assets;assets',
    '--hidden-import=PyQt5',
    '--hidden-import=cv2',
    '--hidden-import=numpy',
    '--clean',
])

print("\nBuild complete! Check the 'dist' folder.")
