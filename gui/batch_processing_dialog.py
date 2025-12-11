from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QListWidget, QComboBox, QGroupBox,
                             QFileDialog, QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import cv2
import os


class BatchWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    
    def __init__(self, files, filter_name, output_dir, processor):
        super().__init__()
        self.files = files
        self.filter_name = filter_name
        self.output_dir = output_dir
        self.processor = processor
        
    def run(self):
        total = len(self.files)
        if total == 0:
            self.finished.emit()
            return
            
        for i, fpath in enumerate(self.files):
            try:
                img = cv2.imread(fpath)
                if img is not None:
                    processed = self.processor.apply_filter(img, self.filter_name)
                    fname = os.path.basename(fpath)
                    name, ext = os.path.splitext(fname)
                    out_path = os.path.join(self.output_dir, f"{name}_out{ext}")
                    cv2.imwrite(out_path, processed)
                    
                self.progress.emit(int((i + 1) / total * 100))
            except Exception:
                continue
                
        self.finished.emit()


class BatchProcessingDialog(QDialog):
    def __init__(self, processor, parent=None):
        super().__init__(parent)
        self.processor = processor
        self.files = []
        self.output_dir = None
        self.setWindowTitle("Batch Processing")
        self.setGeometry(200, 200, 600, 500)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        files_grp = QGroupBox("Input Files")
        files_lay = QVBoxLayout()
        
        self.file_list = QListWidget()
        files_lay.addWidget(self.file_list)
        
        btn_lay = QHBoxLayout()
        add_btn = QPushButton("Add Files")
        add_btn.clicked.connect(self._add_files)
        btn_lay.addWidget(add_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._clear_files)
        btn_lay.addWidget(clear_btn)
        
        files_lay.addLayout(btn_lay)
        files_grp.setLayout(files_lay)
        layout.addWidget(files_grp)
        
        filter_grp = QGroupBox("Filter")
        filter_lay = QHBoxLayout()
        filter_lay.addWidget(QLabel("Filter:"))
        self.filter_cb = QComboBox()
        self.filter_cb.addItems([
            "blur", "sharpen", "edge", "emboss",
            "grayscale", "sepia", "invert", "cartoon"
        ])
        filter_lay.addWidget(self.filter_cb)
        filter_grp.setLayout(filter_lay)
        layout.addWidget(filter_grp)
        
        out_grp = QGroupBox("Output Folder")
        out_lay = QHBoxLayout()
        self.out_label = QLabel("Not selected")
        out_lay.addWidget(self.out_label)
        out_btn = QPushButton("Browse")
        out_btn.clicked.connect(self._select_output)
        out_lay.addWidget(out_btn)
        out_grp.setLayout(out_lay)
        layout.addWidget(out_grp)
        
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        
        action_lay = QHBoxLayout()
        self.run_btn = QPushButton("Start")
        self.run_btn.clicked.connect(self._start)
        action_lay.addWidget(self.run_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        action_lay.addWidget(close_btn)
        layout.addLayout(action_lay)
        
    def _add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if files:
            self.files.extend(files)
            for f in files:
                self.file_list.addItem(os.path.basename(f))
                
    def _clear_files(self):
        self.files.clear()
        self.file_list.clear()
        
    def _select_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_dir = folder
            self.out_label.setText(folder)
            
    def _start(self):
        if not self.files:
            QMessageBox.warning(self, "Error", "No files selected")
            return
            
        if not self.output_dir:
            QMessageBox.warning(self, "Error", "No output folder selected")
            return
            
        self.run_btn.setEnabled(False)
        self.worker = BatchWorker(
            self.files,
            self.filter_cb.currentText(),
            self.output_dir,
            self.processor
        )
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self._on_done)
        self.worker.start()
        
    def _on_done(self):
        self.run_btn.setEnabled(True)
        QMessageBox.information(self, "Done", "Processing completed")
