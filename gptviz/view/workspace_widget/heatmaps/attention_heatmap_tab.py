import numpy as np
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSizePolicy)
from PyQt6.QtCore import Qt

from ....config import settings
from .attention_heatmap_canvas import MplCanvas
from .attention_heatmap_bottom_toolbar import CustomNavigationToolbar
from .attention_toolbar import AttentionControls

class AttentionHeatmapView(QWidget):
    """
    Vista dettagliata per una singola head.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.view_model = None
        self.im_ref = None          
        self.current_data_matrix = None 
        self.current_labels = [] 
        self.max_labels_threshold = 25 

        self._setup_ui()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0) 
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: #181818;")

        self.controls = AttentionControls(
            parent=self, 
            show_head_selector=True, 
            show_save_button=True 
        )
        
        self.controls.mode_changed.connect(self._on_mode_changed)
        self.controls.head_changed.connect(lambda _: self._draw_heatmap())
        self.controls.gamma_changed.connect(lambda _: self._draw_heatmap())
        self.controls.normalize_toggled.connect(lambda _: self._draw_heatmap())
        
        self.layout.addWidget(self.controls)

        self.canvas = MplCanvas(self, width=6, height=6, dpi=100)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.mpl_connect("motion_notify_event", self._on_mouse_hover)
        self.layout.addWidget(self.canvas)

        self.lbl_status = QLabel("Hover over the heatmap to see details")
        self.lbl_status.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.lbl_status)

        self.mpl_toolbar = CustomNavigationToolbar(self.canvas, self)
        self.layout.addWidget(self.mpl_toolbar)

    def set_view_model(self, view_model):
        self.view_model = view_model
        if not self.view_model: return

        self.controls.set_heads(self.view_model.get_num_heads())
        self.im_ref = None
        self._draw_heatmap()

    def _on_mode_changed(self, index):
        # Resetta im_ref per forzare il ridisegno completo
        self.im_ref = None 
        self._draw_heatmap()

    def _draw_heatmap(self):
        if not self.view_model: return

        head_idx = self.controls.get_current_head_index()
        gamma = self.controls.get_current_gamma()
        is_action_mode = (self.controls.get_view_mode_index() == 1)

        # Recupero dati
        if is_action_mode:
            normalize = self.controls.is_normalization_enabled()
            self.current_data_matrix = self.view_model.get_aggregated_matrix(
                head_idx, normalize_by_row=normalize
            )
            self.current_labels = self.view_model.actions
        else:
            self.current_data_matrix = self.view_model.get_raw_matrix(head_idx)
            self.current_labels = self.view_model.tokens

        if self.current_data_matrix is None: return

        matrix_processed = np.power(self.current_data_matrix, gamma)
        ax = self.canvas.axes

        # Se l'immagine esiste e la shape è identica aggiorniamo solo i dati.
        if self.im_ref is not None and self.im_ref.get_array().shape == matrix_processed.shape:
            self.im_ref.set_data(matrix_processed)
            self.im_ref.set_clim(vmin=0, vmax=1)
            self.canvas.draw()
            return

        # altrimenti ridisegno tutto
        ax.clear()
        self.im_ref = ax.imshow(
            matrix_processed,
            aspect='equal', 
            cmap='magma',
            interpolation='nearest',
            vmin=0, vmax=1
        )
        
        mode_str = "Action Attention" if is_action_mode else "Token Attention"
        ax.set_title(f"Head {head_idx} - {mode_str}", color='white', pad=10, fontsize=10)

        if not hasattr(self, 'cbar'):
            self.cbar = self.canvas.fig.colorbar(self.im_ref, ax=ax, fraction=0.046, pad=0.04)
            self.cbar.outline.set_visible(False)
            self.cbar.ax.tick_params(labelsize=8, colors='#888888')

        for spine in ax.spines.values(): spine.set_visible(False)
        ax.set_anchor('C')

        ax.callbacks.connect('xlim_changed', self._update_labels_dynamic)
        ax.callbacks.connect('ylim_changed', self._update_labels_dynamic)

        self._update_labels_dynamic(ax)
        self.canvas.draw()

    def _update_labels_dynamic(self, ax):
        if self.current_data_matrix is None: return
        
        N = self.current_data_matrix.shape[0]
        x_start, x_end = ax.get_xlim()
        visible_range = abs(x_end - x_start)
        
        mode = "LABELS" if visible_range <= self.max_labels_threshold else "TICKS"
        
        idx_start = max(0, int(min(x_start, x_end)))
        idx_end = min(N, int(max(x_start, x_end)) + 1)
        
        if mode == "TICKS":
            step = max(1, int(visible_range // 10))
            ticks = np.arange(0, N, step)
            ax.set_xticks(ticks); ax.set_yticks(ticks)
            ax.set_xticklabels(ticks, fontsize=8, color='#666')
            ax.set_yticklabels(ticks, fontsize=8, color='#666')
        else:
            visible_indices = np.arange(idx_start, idx_end)
            visible_indices = visible_indices[visible_indices < N]
            
            if len(visible_indices) > 0:
                labels = [str(self.current_labels[i]) for i in visible_indices]
                ax.set_xticks(visible_indices)
                ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8, color='#aaaaaa')
                
                y_start, y_end = ax.get_ylim()
                idy_start = max(0, int(min(y_start, y_end)))
                idy_end = min(N, int(max(y_start, y_end)) + 1)
                y_indices = np.arange(idy_start, idy_end)
                y_indices = y_indices[y_indices < N]
                y_labels = [str(self.current_labels[i]) for i in y_indices]
                ax.set_yticks(y_indices)
                ax.set_yticklabels(y_labels, fontsize=8, color='#aaaaaa')

    def _on_mouse_hover(self, event):
        if event.inaxes != self.canvas.axes or self.im_ref is None:
            self.lbl_status.setText("Hover over to see details")
            return
            
        x_idx = int(event.xdata + 0.5)
        y_idx = int(event.ydata + 0.5)
        
        if x_idx < 0 or x_idx >= len(self.current_labels) or y_idx < 0 or y_idx >= len(self.current_labels):
            return
        
        label_src = self.current_labels[y_idx]
        label_tgt = self.current_labels[x_idx]
        val = self.current_data_matrix[y_idx, x_idx]
        
        is_action_mode = (self.controls.get_view_mode_index() == 1)
        prefix = "Action" if is_action_mode else "Token"
        self.lbl_status.setText(f"[{prefix}] {label_src} -> {label_tgt} | Attention: {val:.4f}")