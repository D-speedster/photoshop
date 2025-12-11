from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QListWidgetItem, QGroupBox)
from PyQt5.QtCore import pyqtSignal
import cv2


class LayersPanel(QWidget):
    layer_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.layers = []
        self.current_idx = -1
        self.setMaximumWidth(170)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        grp = QGroupBox("Layers")
        grp_lay = QVBoxLayout()
        
        self.layer_list = QListWidget()
        self.layer_list.currentRowChanged.connect(self._on_select)
        grp_lay.addWidget(self.layer_list)
        
        btn_lay = QHBoxLayout()
        
        add_btn = QPushButton("+")
        add_btn.setToolTip("New layer")
        add_btn.clicked.connect(self._add_layer)
        btn_lay.addWidget(add_btn)
        
        del_btn = QPushButton("-")
        del_btn.setToolTip("Delete layer")
        del_btn.clicked.connect(self._delete_layer)
        btn_lay.addWidget(del_btn)
        
        merge_btn = QPushButton("M")
        merge_btn.setToolTip("Merge down")
        merge_btn.clicked.connect(self._merge_down)
        btn_lay.addWidget(merge_btn)
        
        grp_lay.addLayout(btn_lay)
        grp.setLayout(grp_lay)
        layout.addWidget(grp)
        layout.addStretch()
        
    def _add_layer(self):
        if self.main_window and self.main_window.current_image is not None:
            layer = self.main_window.current_image.copy()
            self.layers.append(layer)
            item = QListWidgetItem(f"Layer {len(self.layers)}")
            self.layer_list.addItem(item)
            self.layer_list.setCurrentRow(len(self.layers) - 1)
            
    def _delete_layer(self):
        if self.current_idx >= 0 and len(self.layers) > 1:
            del self.layers[self.current_idx]
            self.layer_list.takeItem(self.current_idx)
            self._update_composite()
            
    def _merge_down(self):
        if self.current_idx > 0:
            bottom = self.layers[self.current_idx - 1]
            top = self.layers[self.current_idx]
            
            if bottom.shape != top.shape:
                top = cv2.resize(top, (bottom.shape[1], bottom.shape[0]))
                
            merged = cv2.addWeighted(bottom, 0.5, top, 0.5, 0)
            self.layers[self.current_idx - 1] = merged
            del self.layers[self.current_idx]
            self.layer_list.takeItem(self.current_idx)
            self._update_composite()
            
    def _on_select(self, idx):
        self.current_idx = idx
        if 0 <= idx < len(self.layers):
            self.main_window.current_image = self.layers[idx]
            self.main_window.display_image(self.layers[idx])
            
    def _update_composite(self):
        if self.layers:
            self.layer_changed.emit()
            
    def get_composite(self):
        if not self.layers:
            return None
        result = self.layers[0].copy()
        for layer in self.layers[1:]:
            if layer.shape != result.shape:
                layer = cv2.resize(layer, (result.shape[1], result.shape[0]))
            result = cv2.addWeighted(result, 0.5, layer, 0.5, 0)
        return result
