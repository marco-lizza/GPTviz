# src/views/heatmap_view.py
import numpy as np
import torch
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QDoubleSpinBox, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Importiamo le nostre classi custom
from .ui.canvas import MplCanvas
from .ui.heatmap_toolbar import CustomNavigationToolbar

class AttentionHeatmapView(QWidget):
    """
    Vista principale per la visualizzazione delle matrici di attenzione (Heatmap).

    Gestisce:
    - Il rendering della matrice tramite Matplotlib.
    - La navigazione interattiva (Zoom, Pan) con limiti bloccati (Clamping).
    - La visualizzazione dinamica delle etichette (nomi dei token vs indici numerici).
    - La selezione della testa di attenzione (Head) e la correzione Gamma.
    """
    def __init__(self, parent=None):
        """
        Inizializza l'interfaccia utente, il canvas, la toolbar e i controlli.

        Args:
            parent (QWidget, optional): Il widget genitore. Default è None.
        """
        super().__init__(parent)
        
        # --- Stato Interno ---
        self.data_layers = []       
        self.current_tokens = []    
        self.im_ref = None          
        self.current_raw_matrix = None 
        self.max_labels_threshold = 30 

        # --- Layout ---
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # --- Toolbar Controlli (Head/Gamma) ---
        self._init_controls()

        # --- Canvas ---
        self.canvas = MplCanvas(self, width=6, height=6, dpi=100)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.mpl_connect("motion_notify_event", self._on_mouse_hover)
        self.layout.addWidget(self.canvas)

        # --- Info Bar ---
        self.lbl_status = QLabel("Hover over the heatmap to see details")
        self.lbl_status.setStyleSheet("background-color: #222; color: #00ff00; padding: 4px; font-weight: bold; font-family: monospace;")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.lbl_status)

        # --- Matplotlib Toolbar Custom ---
        self.mpl_toolbar = CustomNavigationToolbar(self.canvas, self)
        self.layout.addWidget(self.mpl_toolbar)

    def _init_controls(self):
        """
        Crea e posiziona i widget di controllo nella parte superiore della vista.
        Include il menu a tendina per le 'Head' e lo SpinBox per il valore 'Gamma'.
        """
        controls_widget = QWidget()
        controls_widget.setStyleSheet("background-color: #333333; color: white;")
        controls_layout = QHBoxLayout(controls_widget)

        controls_layout.addWidget(QLabel("Head:"))
        self.combo_heads = QComboBox()
        self.combo_heads.setMinimumWidth(80)
        self.combo_heads.currentIndexChanged.connect(self._draw_heatmap)
        controls_layout.addWidget(self.combo_heads)

        controls_layout.addSpacing(15)

        controls_layout.addWidget(QLabel("Gamma:"))
        self.spin_gamma = QDoubleSpinBox()
        self.spin_gamma.setRange(0.1, 5.0)
        self.spin_gamma.setSingleStep(0.1)
        self.spin_gamma.setValue(1.0)
        self.spin_gamma.valueChanged.connect(self._draw_heatmap)
        controls_layout.addWidget(self.spin_gamma)
        
        controls_layout.addStretch()
        self.layout.addWidget(controls_widget)

    def update_data(self, heads_attention_list, token_list):
        """
        Aggiorna la vista con nuovi dati di attenzione e token.

        Resetta lo stato interno, processa i tensori convertendoli in numpy array,
        e ripopola il menu a tendina delle teste (Heads).

        Args:
            heads_attention_list (list): Lista di tensori (torch.Tensor) o array numpy 
                                         rappresentanti le matrici di attenzione.
            token_list (list[str]): Lista delle stringhe dei token corrispondenti.
        """
        if not heads_attention_list: return

        self.data_layers = []
        self.current_tokens = token_list
        self.im_ref = None 
        self.current_raw_matrix = None

        for tensor in heads_attention_list:
            if isinstance(tensor, torch.Tensor):
                self.data_layers.append(tensor.detach().cpu().squeeze().numpy())
            else:
                self.data_layers.append(tensor)

        self.combo_heads.blockSignals(True)
        self.combo_heads.clear()
        for i in range(len(self.data_layers)):
            icon_path = "assets/attention_navigator/item_icons/head.svg" 
            icon = QIcon(icon_path)
            
            self.combo_heads.addItem(icon, f"Head {i}")
        self.combo_heads.blockSignals(False)

        if self.combo_heads.count() > 0:
            self.combo_heads.setCurrentIndex(0)
            self._draw_heatmap()

    def _draw_heatmap(self):
        """
        Disegna o aggiorna la Heatmap corrente sul canvas.
        """
        head_idx = self.combo_heads.currentIndex()
        gamma = self.spin_gamma.value()

        if head_idx < 0 or head_idx >= len(self.data_layers): return

        self.current_raw_matrix = self.data_layers[head_idx]
        matrix_processed = np.power(self.current_raw_matrix, gamma)

        ax = self.canvas.axes
        
        # Aggiornamento rapido
        if self.im_ref is not None and self.im_ref.get_array().shape == matrix_processed.shape:
            self.im_ref.set_data(matrix_processed)
            self.im_ref.set_clim(vmin=0, vmax=1)
            self.canvas.draw()
            return

        # Setup completo
        ax.clear()
        self.im_ref = ax.imshow(
            matrix_processed,
            aspect='equal', 
            cmap='magma', 
            interpolation='nearest',
            vmin=0, vmax=1
        )
        
        ax.set_title(f"Head {head_idx}", color='white', pad=10, fontsize=10)

        if not hasattr(self, 'cbar'):
            self.cbar = self.canvas.fig.colorbar(self.im_ref, ax=ax, fraction=0.046, pad=0.04)
            self.cbar.outline.set_visible(False)
            self.cbar.ax.tick_params(labelsize=8, colors='#888888')

        for spine in ax.spines.values(): spine.set_visible(False)

        # Importante per il centramento
        ax.set_anchor('C')

        ax.callbacks.connect('xlim_changed', self._update_labels_dynamic)
        ax.callbacks.connect('ylim_changed', self._update_labels_dynamic)

        self._update_labels_dynamic(ax)
        self.canvas.draw()

    def _update_labels_dynamic(self, ax):
        """
        Gestisce dinamicamente le etichette degli assi e limita il movimento (Clamping).

        Questa funzione viene chiamata ad ogni evento di Zoom o Pan.
        
        Funzionalità:
        1. Clamping: Impedisce all'utente di trascinare la vista oltre i bordi 
           fisici della matrice (spazio vuoto), forzando i limiti degli assi.
        2. Labeling Dinamico: - Se lo zoom è alto (pochi token visibili): Mostra i nomi dei token ruotati a 45°.
           - Se lo zoom è basso (molti token visibili): Mostra indici numerici sparsi.
        3. Anti-Jitter: Minimizza gli scatti visivi durante il cambio di modalità label.

        Args:
            ax (matplotlib.axes.Axes): Gli assi su cui operare.
        """
        if self.current_raw_matrix is None: return

        # --- 1. CLAMPING LOGIC (Limita il movimento ai bordi) ---
        N = self.current_raw_matrix.shape[0]
        min_bound, max_bound = -0.5, N - 0.5
        
        x_start, x_end = ax.get_xlim()
        span_x = x_end - x_start

        if abs(span_x) >= (max_bound - min_bound):
            new_x_start, new_x_end = min_bound, max_bound
        else:
            new_x_start, new_x_end = x_start, x_end
            if new_x_start < min_bound:
                new_x_start = min_bound
                new_x_end = min_bound + span_x
            elif new_x_end > max_bound:
                new_x_end = max_bound
                new_x_start = max_bound - span_x

        y_start, y_end = ax.get_ylim()
        is_inverted = (y_start > y_end)
        curr_y_min, curr_y_max = min(y_start, y_end), max(y_start, y_end)
        curr_span_y = curr_y_max - curr_y_min

        if curr_span_y >= (max_bound - min_bound):
            corr_y_min, corr_y_max = min_bound, max_bound
        else:
            corr_y_min, corr_y_max = curr_y_min, curr_y_max
            if corr_y_min < min_bound:
                corr_y_min = min_bound
                corr_y_max = min_bound + curr_span_y
            elif corr_y_max > max_bound:
                corr_y_max = max_bound
                corr_y_min = max_bound - curr_span_y

        new_y_start, new_y_end = (corr_y_max, corr_y_min) if is_inverted else (corr_y_min, corr_y_max)

        if (abs(new_x_start - x_start) > 1e-5 or abs(new_x_end - x_end) > 1e-5):
            ax.set_xlim(new_x_start, new_x_end)
            return 
        if (abs(new_y_start - y_start) > 1e-5 or abs(new_y_end - y_end) > 1e-5):
            ax.set_ylim(new_y_start, new_y_end)
            return

        # --- 2. LABELS LOGIC ---
        visible_x_range = abs(new_x_end - new_x_start)
        current_mode = "LABELS" if visible_x_range <= self.max_labels_threshold else "TICKS"
        
        last_mode = getattr(ax, '_last_label_mode', None)
        if current_mode == "TICKS" and last_mode == "TICKS": pass 
        ax._last_label_mode = current_mode

        idx_start = max(0, int(min(new_x_start, new_x_end)))
        idx_end = min(N, int(max(new_x_start, new_x_end)) + 1)
        idy_start = max(0, int(min(new_y_start, new_y_end)))
        idy_end = min(N, int(max(new_y_start, new_y_end)) + 1)

        if current_mode == "LABELS":
            x_ticks = np.arange(idx_start, idx_end)
            x_ticks = x_ticks[x_ticks < N]
            y_ticks = np.arange(idy_start, idy_end)
            y_ticks = y_ticks[y_ticks < N]

            if len(x_ticks) > 0:
                labels_x = [self.current_tokens[i] for i in x_ticks]
                ax.set_xticks(x_ticks)
                ax.set_xticklabels(labels_x, rotation=45, ha='right', rotation_mode='anchor', fontsize=8, color='#aaaaaa')
                
                labels_y = [self.current_tokens[i] for i in y_ticks]
                ax.set_yticks(y_ticks)
                ax.set_yticklabels(labels_y, fontsize=8, color='#aaaaaa')
        else:
            step = max(5, int(visible_x_range // 10)) 
            ticks = np.arange(0, N, step)
            ax.set_xticks(ticks)
            ax.set_xticklabels(ticks, rotation=0, fontsize=8, color='#666')
            ax.set_yticks(ticks)
            ax.set_yticklabels(ticks, fontsize=8, color='#666')

    def _on_mouse_hover(self, event):
        """
        Gestisce l'evento di movimento del mouse sopra il canvas (Tooltip).

        Se il mouse è sopra la matrice, recupera le coordinate, identifica
        i token corrispondenti e il valore di attenzione reale
        (dalla matrice originale senza correzione Gamma), aggiornando la status bar.

        Args:
            event (matplotlib.backend_bases.MouseEvent): L'evento mouse generato da Matplotlib.
        """
        if event.inaxes != self.canvas.axes or self.im_ref is None:
            self.lbl_status.setText("Hover over the heatmap to see details")
            return
        x_idx = int(event.xdata + 0.5)
        y_idx = int(event.ydata + 0.5)
        if x_idx < 0 or x_idx >= len(self.current_tokens) or y_idx < 0 or y_idx >= len(self.current_tokens):
            return
        
        token_y = self.current_tokens[y_idx]
        token_x = self.current_tokens[x_idx]
        real_val = self.current_raw_matrix[y_idx, x_idx] if self.current_raw_matrix is not None else 0.0
        self.lbl_status.setText(f"{token_y} -> {token_x} | Val: {real_val:.4f}")