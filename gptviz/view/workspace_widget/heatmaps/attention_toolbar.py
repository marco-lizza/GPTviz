from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QComboBox, 
                             QDoubleSpinBox, QFrame, QCheckBox, QPushButton)
from PyQt6.QtCore import pyqtSignal, QSize, Qt
from PyQt6.QtGui import QIcon

from ....config import settings

class AttentionControls(QFrame):
    """
    Toolbar condivisa per le viste di Attenzione.
    Gestisce Head, Gamma, Mode, Normalizzazione e Salvataggio.
    """
    
    head_changed = pyqtSignal(int)      
    gamma_changed = pyqtSignal(float)
    mode_changed = pyqtSignal(int) 
    normalize_toggled = pyqtSignal(bool)
    save_clicked = pyqtSignal()          

    def __init__(self, parent=None, show_head_selector=True, show_save_button=False):
        super().__init__(parent)
        self.show_head_selector = show_head_selector
        self.show_save_button = show_save_button
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5) 
        layout.setSpacing(15)
        
        self.setStyleSheet("background-color: #181818; color: #dddddd;")

        if self.show_head_selector:
            head_label = QLabel("HEAD:")
            head_label.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))
            layout.addWidget(head_label)

            self.combo_heads = QComboBox()
            self.combo_heads.setMinimumWidth(100)
            self.combo_heads.setStyleSheet(settings.get_stylesheets("QComboBox_style.qss"))
            self.combo_heads.currentIndexChanged.connect(self.head_changed.emit)
            layout.addWidget(self.combo_heads)

        gamma_label = QLabel("GAMMA:")
        gamma_label.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))
        layout.addWidget(gamma_label)

        self.spin_gamma = QDoubleSpinBox()
        self.spin_gamma.setRange(0.1, 5.0)
        self.spin_gamma.setSingleStep(0.1)
        self.spin_gamma.setValue(1.0)
        self.spin_gamma.setStyleSheet(settings.get_stylesheet("QSpinBox_style.qss"))
        self.spin_gamma.valueChanged.connect(self.gamma_changed.emit)
        layout.addWidget(self.spin_gamma)

        layout.addSpacing(10)

        mode_label = QLabel("MODE:")
        mode_label.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))
        layout.addWidget(mode_label)

        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["Token", "Action"])
        
        self.combo_mode.setStyleSheet(settings.get_stylesheets("QComboBox_style.qss"))
        self.combo_mode.currentIndexChanged.connect(self._on_internal_mode_changed)
        layout.addWidget(self.combo_mode)

        self.chk_normalize = QCheckBox("Prob. (row=1):")
        self.chk_normalize.setStyleSheet(settings.get_stylesheets("QCheckBox_style.qss"))
        self.chk_normalize.setChecked(True)
        self.chk_normalize.setVisible(False) 
        self.chk_normalize.toggled.connect(self.normalize_toggled.emit)
        layout.addWidget(self.chk_normalize)
        
        layout.addStretch()

        if self.show_save_button:
            btn_save = QPushButton()
            if QIcon("gptviz/resources/assets/utility/save.svg").isNull():
                btn_save.setText("Save")
            else:
                btn_save.setIcon(QIcon("gptviz/resources/assets/utility/save.svg"))
                btn_save.setIconSize(QSize(22, 22))
                
            btn_save.setStyleSheet("""
                QPushButton {
                    background-color: #3d3d3d;
                    color: white;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 4px 8px;
                }
                QPushButton:hover { background-color: #4d4d4d; }
            """)
            btn_save.clicked.connect(self.save_clicked.emit)
            layout.addWidget(btn_save)

    def _on_internal_mode_changed(self, index):
        """Gestisce visibilità checkbox e propaga il segnale."""
        is_action_mode = (index == 1)
        self.chk_normalize.setVisible(is_action_mode)
        self.mode_changed.emit(index)

    def set_heads(self, count: int):
        if not self.show_head_selector: return
        self.combo_heads.blockSignals(True) 
        self.combo_heads.clear()
        icon = QIcon("gptviz/resources/assets/attention_navigator/item_icons/head.svg")
        for i in range(count):
            self.combo_heads.addItem(icon, f"Head {i}")
        self.combo_heads.blockSignals(False)
        if count > 0: self.combo_heads.setCurrentIndex(0)
    
    def get_current_head_index(self) -> int:
        if not self.show_head_selector: return -1
        return self.combo_heads.currentIndex()

    def get_current_gamma(self) -> float:
        return self.spin_gamma.value()
    
    def get_view_mode_index(self) -> int:
        return self.combo_mode.currentIndex()

    def is_normalization_enabled(self) -> bool:
        return self.chk_normalize.isChecked()