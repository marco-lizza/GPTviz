import math
import numpy as np
import torch
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QDoubleSpinBox, QFrame, QSizePolicy,QPushButton,QFileDialog)
from PyQt6.QtCore import Qt,QSize
from PyQt6.QtGui import QIcon

import matplotlib.cm as cm
import matplotlib.colors as mcolors

from .ui.canvas import MplCanvas
from src.config import settings

class MultiHeadAttentionView(QWidget):
    """
    Vista a griglia per tutte le head.
    
    OTTIMIZZAZIONE:
    Utilizza un approccio 'Stateful'. Mantiene i riferimenti agli oggetti grafici (AxesImage)
    e aggiorna solo i pixel (set_data) quando cambia il Gamma, evitando di 
    ricostruire l'intera figura Matplotlib.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # --- Stato Interno ---
        self.raw_data = []
        self.image_refs = []

        # --- Layout ---
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: #181818;")

        self._init_toolbar()

        self.canvas = MplCanvas(self, width=8, height=8, dpi=100)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.canvas)

    def _init_toolbar(self):
        """Inizializza la barra superiore con Gamma e Pulsante Salva."""
        toolbar = QFrame()
        toolbar.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))
        
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(10, 5, 10, 5)
        tb_layout.setSpacing(15)

        # --- GAMMA ---
        lbl_gamma = QLabel("GAMMA:")
        lbl_gamma.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))
        tb_layout.addWidget(lbl_gamma)

        self.spin_gamma = QDoubleSpinBox()
        self.spin_gamma.setRange(0.1, 5.0)
        self.spin_gamma.setSingleStep(0.1)
        self.spin_gamma.setValue(1.0)
        self.spin_gamma.setStyleSheet(settings.get_stylesheet("QDoubleSpinBox_style.qss"))
        self.spin_gamma.valueChanged.connect(self._refresh_pixel_data)
        tb_layout.addWidget(self.spin_gamma)
        
        # Spacer: Spinge il pulsante Save a destra
        tb_layout.addStretch()

        # --- SALVA ---
        btn_save = QPushButton()
        
        icon_path = "assets/utility/save.svg" 
        btn_save.setIcon(QIcon(icon_path))
        
        btn_save.setIconSize(QSize(25, 25)) 
        btn_save.setStyleSheet(settings.get_stylesheet("QPushButton_style.qss"))
        
        btn_save.clicked.connect(self.save_grid)
        tb_layout.addWidget(btn_save)

        self.layout.addWidget(toolbar)

    def save_grid(self):
        """
        Apre un dialogo per salvare l'intera griglia come immagine.
        """
        if not self.image_refs: return # Nessun dato da salvare

        # Apre il dialogo di sistema
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Salva Griglia Attenzione", 
            "attention_grid.png", 
            "Images (*.png *.jpg *.pdf *.svg)"
        )

        if file_path:
            # dpi=300 garantisce alta qualità per pubblicazioni
            # facecolor garantisce che lo sfondo scuro venga salvato (o usa 'none' per trasparenza)
            bg_color = self.canvas.fig.get_facecolor()
            self.canvas.fig.savefig(file_path, bbox_inches='tight', dpi=300, facecolor=bg_color)
            print(f"Griglia salvata in: {file_path}")

    def update_data(self, heads_attention_list):
        """
        Riceve i nuovi dati. Decide se ricostruire la griglia o aggiornare solo i dati.
        """
        if not heads_attention_list: return

        new_data = []
        for tensor in heads_attention_list:
            if isinstance(tensor, torch.Tensor):
                new_data.append(tensor.detach().cpu().squeeze().numpy())
            else:
                new_data.append(tensor)
        
        self.raw_data = new_data

        # Se il numero di head è cambiato (o è la prima volta), dobbiamo rifare la struttura
        if len(self.image_refs) != len(self.raw_data):
            self._rebuild_grid_structure()
        else:
            # Se la struttura è uguale, aggiorniamo solo i pixel
            self._refresh_pixel_data()

    def _rebuild_grid_structure(self):
        """
        Ricostruisce layout, assi e oggetti grafici.
        """
        n_heads = len(self.raw_data)
        if n_heads == 0: return

        self.image_refs = [] 
        self.canvas.fig.clear()

        cols = int(math.ceil(math.sqrt(n_heads)))
        rows = int(math.ceil(n_heads / cols))

        axes = self.canvas.fig.subplots(rows, cols)
        if n_heads == 1: axes = np.array([axes])
        ax_flat = axes.flat

        # Creazione matrici
        for i, ax in enumerate(ax_flat):
            if i < n_heads:
                im = ax.imshow(self.raw_data[i], cmap='magma', vmin=0, vmax=1, interpolation='nearest')
                self.image_refs.append(im)
                
                ax.set_title(f"Head {i}", fontsize=8, color='white', pad=0)
                ax.axis('off')
            else:
                ax.axis('off')
                ax.set_visible(False)

        # Colorbar
        self.canvas.fig.subplots_adjust(left=0.05, right=0.9, top=0.95, bottom=0.05, wspace=0.1, hspace=0.2)
        cbar_ax = self.canvas.fig.add_axes([0.92, 0.1, 0.02, 0.8])
        
        norm = mcolors.Normalize(vmin=0, vmax=1)
        sm = cm.ScalarMappable(cmap='magma', norm=norm)
        sm.set_array([]) 
        
        cbar = self.canvas.fig.colorbar(sm, cax=cbar_ax)
        
        cbar.outline.set_visible(False)
        cbar.ax.tick_params(labelsize=8, colors='#888888')

        self._refresh_pixel_data()

    def _refresh_pixel_data(self):
        """
        Aggiorna solo i dati delle immagini esistenti.
        Viene chiamato quando l'utente muove lo slider Gamma.
        """
        if not self.image_refs or not self.raw_data: return

        gamma = self.spin_gamma.value()

        for raw_matrix, img_obj in zip(self.raw_data, self.image_refs):
            
            processed_matrix = np.power(raw_matrix, gamma)
            img_obj.set_data(processed_matrix)

        # Unico comando di redraw alla fine
        self.canvas.draw()