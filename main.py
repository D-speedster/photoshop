"""
Photo Editor - Professional Image Editing Application
Copyright (c) 2024 D-speedster (github.com/D-speedster)
Licensed under MIT License
"""
import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Photo Editor")
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
