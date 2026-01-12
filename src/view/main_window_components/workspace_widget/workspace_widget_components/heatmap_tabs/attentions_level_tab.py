import math
import numpy as np
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QSizePolicy, QFileDialog)
from PyQt6.QtCore import Qt
import matplotlib.cm as cm
import matplotlib.colors as mcolors

from .ui_utils.attention_heatmap_canvas import MplCanvas
from .ui_utils.attention_toolbar import AttentionControls

class MultiHeadAttentionView(QWidget):
    """
    Vista a griglia per tutte le head.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.view_model = None
        self.image_refs = []

        # Setup Layout
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
        # Configurazione: NO Head Selector, SI Save Button
        self.controls = AttentionControls(
            parent=self, 
            show_head_selector=False, 
            show_save_button=True
        )
        
        # --- CONNESSIONE SEGNALI ---
        
        # 1. Mode Change -> Dimensioni cambiano -> REBUILD COMPLETO
        self.controls.mode_changed.connect(self._rebuild_grid_structure)
        
        # 2. Normalizzazione -> Dimensioni uguali -> AGGIORNAMENTO RAPIDO (Pixel)
        self.controls.normalize_toggled.connect(self._refresh_pixel_data)
        
        # 3. Gamma -> AGGIORNAMENTO RAPIDO (Pixel)
        self.controls.gamma_changed.connect(self._refresh_pixel_data)
        
        # 4. Save
        self.controls.save_clicked.connect(self.save_grid)
        
        self.layout.addWidget(self.controls)

    def set_view_model(self, view_model):
        self.view_model = view_model
        if self.view_model and self.view_model.get_num_heads() > 0:
            self._rebuild_grid_structure()

    def _fetch_data_for_head(self, head_idx):
        """Recupera la matrice corretta dal ViewModel basandosi sui controlli."""
        if not self.view_model: return None
        
        is_action_mode = (self.controls.get_view_mode_index() == 1)
        
        if is_action_mode:
            return self.view_model.get_aggregated_matrix(
                head_idx, 
                normalize_by_row=self.controls.is_normalization_enabled()
            )
        else:
            return self.view_model.get_raw_matrix(head_idx)

    def _rebuild_grid_structure(self):
        """Ricostruisce layout, assi e oggetti grafici (Slow Path)."""
        if not self.view_model: return
        n_heads = self.view_model.get_num_heads()
        if n_heads == 0: return

        self.image_refs = [] 
        self.canvas.fig.clear()

        cols = int(math.ceil(math.sqrt(n_heads)))
        rows = int(math.ceil(n_heads / cols))

        axes = self.canvas.fig.subplots(rows, cols)
        if n_heads == 1: axes = np.array([axes])
        ax_flat = axes.flat

        # Usiamo head 0 per verificare se i dati esistono
        if self._fetch_data_for_head(0) is None: return

        for i, ax in enumerate(ax_flat):
            if i < n_heads:
                data = self._fetch_data_for_head(i)
                # Crea l'immagine iniziale
                im = ax.imshow(data, cmap='magma', vmin=0, vmax=1, interpolation='nearest')
                self.image_refs.append(im)
                
                ax.set_title(f"Head {i}", fontsize=8, color='white', pad=2)
                ax.axis('off')
            else:
                ax.axis('off')
                ax.set_visible(False)

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
        """Aggiorna solo i valori dei pixel (Fast Path)."""
        if not self.image_refs or not self.view_model: return
        
        gamma = self.controls.get_current_gamma()

        for i, img_obj in enumerate(self.image_refs):
            # Recupera i dati aggiornati (es. Prob vs Densità)
            raw_matrix = self._fetch_data_for_head(i)
            
            if raw_matrix is not None:
                processed_matrix = np.power(raw_matrix, gamma)
                img_obj.set_data(processed_matrix)

        self.canvas.draw()

    def save_grid(self):
        if not self.image_refs: return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salva Griglia", "attention_grid.png", "Images (*.png *.jpg *.pdf)"
        )
        if file_path:
            bg_color = self.canvas.fig.get_facecolor()
            self.canvas.fig.savefig(file_path, bbox_inches='tight', dpi=300, facecolor=bg_color)
            print(f"Griglia salvata in: {file_path}")