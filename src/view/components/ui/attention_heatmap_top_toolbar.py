from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QComboBox, 
                             QDoubleSpinBox, QFrame)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon

from src.config import settings

class HeatmapControls(QFrame):
    """
    Widget contenitore per i controlli della Heatmap (Selezione Head e Gamma).
    
    Responsabilità:
    - Gestire il layout della toolbar.
    - Caricare gli stili specifici per i controlli.
    - Disaccoppiare la UI dalla logica: emette segnali puri (int/float) 
      invece di costringere la vista principale a leggere i widget.
    """
    
    head_changed = pyqtSignal(int)      
    gamma_changed = pyqtSignal(float)   

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Costruisce l'interfaccia e applica gli stili ai singoli componenti."""
        
        # Layout Orizzontale
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5) 
        layout.setSpacing(15)
        
        # Label "HEAD:"
        head_label = QLabel("HEAD:")
        head_label.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))
        layout.addWidget(head_label)

        # Combo Box
        self.combo_heads = QComboBox()
        stylesheet = settings.get_stylesheets("QComboBox_style.qss")
        self.setStyleSheet(stylesheet)
        self.combo_heads.setMinimumWidth(100)

        # Connettiamo il segnale interno del combo al nostro segnale custom

        self.combo_heads.currentIndexChanged.connect(self.head_changed.emit)
        layout.addWidget(self.combo_heads)

        # Label "GAMMA:"
        gamma_label = QLabel("GAMMA:")
        gamma_label.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))
        layout.addWidget(gamma_label)

        # Spin Box
        self.spin_gamma = QDoubleSpinBox()
        self.spin_gamma.setRange(0.1, 5.0)
        self.spin_gamma.setSingleStep(0.1)
        self.spin_gamma.setValue(1.0)
        
        self.spin_gamma.setStyleSheet(settings.get_stylesheet("QSpinBox_style.qss"))
        
        self.spin_gamma.valueChanged.connect(self.gamma_changed.emit)
        layout.addWidget(self.spin_gamma)
        
        layout.addStretch()

    def set_heads(self, count: int):
        """
        Popola il menu a tendina con le Head disponibili.
        Gestisce il blocco dei segnali per evitare refresh inutili durante l'inizializzazione.
        
        Args:
            count (int): Numero totale di head da visualizzare.
        """
        self.combo_heads.blockSignals(True) 
        self.combo_heads.clear()
        
        icon_path = "assets/attention_navigator/item_icons/head.svg" 
        icon = QIcon(icon_path)

        for i in range(count):
            self.combo_heads.addItem(icon, f"Head {i}")
            
        # Riattiviamo i segnali
        self.combo_heads.blockSignals(False)
        
        # Impostiamo il default sul primo elemento se esiste
        if count > 0:
            self.combo_heads.setCurrentIndex(0)
    
    def get_current_head_index(self) -> int:
        return self.combo_heads.currentIndex()

    def get_current_gamma(self) -> float:
        return self.spin_gamma.value()