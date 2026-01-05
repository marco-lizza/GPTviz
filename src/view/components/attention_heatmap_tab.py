import numpy as np
import torch
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel,QSizePolicy)
from PyQt6.QtCore import Qt

from .ui.attention_heatmap_canvas import MplCanvas
from .ui.attention_heatmap_bottom_toolbar import CustomNavigationToolbar

from src.config import settings
from src.view.components.ui.attention_heatmap_top_toolbar import HeatmapControls

class AttentionHeatmapView(QWidget):
    """
    Vista principale per la visualizzazione delle matrici di attenzione (Heatmap).
    
    Responsabilità:
    - Coordinare i dati (Tensori) con la visualizzazione (Matplotlib).
    - Gestire l'interattività avanzata (Zoom, Pan, Hover).
    - Aggiornare la grafica in risposta ai comandi della Toolbar (Head/Gamma).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.data_layers = []
        self.current_tokens = []
        
        # Permette di aggiornare solo i dati pixel (veloce) invece di ricreare tutto il grafico (lento).
        self.im_ref = None          
        self.current_raw_matrix = None 
        
        # Soglia di zoom: se ci sono meno di 20 token visibili, mostra le etichette di testo.
        # Altrimenti mostra indici numerici per evitare confusione visiva.
        self.max_labels_threshold = 20 

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0) 

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: #181818;")

        # Istanziamo il widget separato che contiene ComboBox e SpinBox
        self.controls = HeatmapControls()
        
        self.controls.head_changed.connect(lambda _: self._draw_heatmap())
        self.controls.gamma_changed.connect(lambda _: self._draw_heatmap())
        self.layout.addWidget(self.controls)

        self.canvas = MplCanvas(self, width=6, height=6, dpi=100)
        
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.canvas.mpl_connect("motion_notify_event", self._on_mouse_hover)
        self.layout.addWidget(self.canvas)

        # Mostra i dettagli del token sotto il cursore
        self.lbl_status = QLabel("Hover over the heatmap to see details")
        stylesheet = settings.get_stylesheet("QLabel_style.qss")
        self.lbl_status.setStyleSheet(stylesheet)
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.lbl_status)

        # La toolbar personalizzata
        self.mpl_toolbar = CustomNavigationToolbar(self.canvas, self)
        self.layout.addWidget(self.mpl_toolbar)

    def update_data(self, heads_attention_list, token_list):
        """
        Riceve nuovi dati dall'esterno.
        Pulisce lo stato precedente e prepara la vista.
        """
        if not heads_attention_list: return

        self.data_layers = []
        self.current_tokens = token_list
        self.im_ref = None 
        self.current_raw_matrix = None

        # Conversione dei tensori PyTorch in array NumPy per Matplotlib
        for tensor in heads_attention_list:
            if isinstance(tensor, torch.Tensor):
                self.data_layers.append(tensor.detach().cpu().squeeze().numpy())
            else:
                self.data_layers.append(tensor)

        self.controls.set_heads(len(self.data_layers))

        # Se ci sono dati, disegniamo subito la prima head (di default indice 0)
        if self.data_layers:
            self._draw_heatmap()

    def _draw_heatmap(self):
        """
        Core Rendering Logic.
        Recupera i parametri dai controlli e renderizza la matrice.
        """
        head_idx = self.controls.get_current_head_index()
        gamma = self.controls.get_current_gamma()

        if head_idx < 0 or head_idx >= len(self.data_layers): return

        self.current_raw_matrix = self.data_layers[head_idx]
        # Applicazione della correzione Gamma per evidenziare i valori bassi/alti
        matrix_processed = np.power(self.current_raw_matrix, gamma)

        ax = self.canvas.axes

        # Se la matrice ha le stesse dimensioni della precedente, aggiorniamo solo i dati pixel.
        if self.im_ref is not None and self.im_ref.get_array().shape == matrix_processed.shape:
            self.im_ref.set_data(matrix_processed)
            self.im_ref.set_clim(vmin=0, vmax=1)
            self.canvas.draw()
            return

        # Pulisce tutto e ricrea l'oggetto immagine. Si fa solo la prima volta o se cambiano le dimensioni.
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

        # Centra il grafico nell'area disponibile
        ax.set_anchor('C')

        ax.callbacks.connect('xlim_changed', self._update_labels_dynamic)
        ax.callbacks.connect('ylim_changed', self._update_labels_dynamic)

        # Prima chiamata per settare le etichette iniziali
        self._update_labels_dynamic(ax)
        self.canvas.draw()

    def _update_labels_dynamic(self, ax):
        """
        Gestisce la logica complessa di navigazione:
        1. Clamping: Blocca la telecamera ai bordi della matrice.
        2. LOD (Level of Detail): Mostra testo o numeri in base allo zoom.
        """
        if self.current_raw_matrix is None: return

        # Evita che l'utente trascini il grafico fuori dalla vista, mostrando lo spazio bianco.
        
        N = self.current_raw_matrix.shape[0]
        min_bound, max_bound = -0.5, N - 0.5
        
        # Recupera i limiti attuali della vista (dopo lo zoom/pan dell'utente)
        x_start, x_end = ax.get_xlim()
        span_x = x_end - x_start

        # Calcolo correzioni asse X
        if abs(span_x) >= (max_bound - min_bound):
            # Se siamo zoomati indietro più della grandezza della matrice, centra tutto
            new_x_start, new_x_end = min_bound, max_bound
        else:
            # Altrimenti, sposta i bordi se escono dai limiti
            new_x_start, new_x_end = x_start, x_end
            if new_x_start < min_bound:
                new_x_start = min_bound
                new_x_end = min_bound + span_x
            elif new_x_end > max_bound:
                new_x_end = max_bound
                new_x_start = max_bound - span_x

        # Calcolo correzioni asse Y (logica identica)
        y_start, y_end = ax.get_ylim()
        is_inverted = (y_start > y_end) # In matplotlib le immagini a volte hanno Y invertita (0 in alto)
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

        # Riapplica l'inversione se necessario
        new_y_start, new_y_end = (corr_y_max, corr_y_min) if is_inverted else (corr_y_min, corr_y_max)

        # Applica i limiti corretti solo se c'è una differenza significativa (evita loop infiniti)
        if (abs(new_x_start - x_start) > 1e-5 or abs(new_x_end - x_end) > 1e-5):
            ax.set_xlim(new_x_start, new_x_end)
            return
        if (abs(new_y_start - y_start) > 1e-5 or abs(new_y_end - y_end) > 1e-5):
            ax.set_ylim(new_y_start, new_y_end)
            return

        # --- GESTIONE ETICHETTE (LOD) ---
        visible_x_range = abs(new_x_end - new_x_start)
        
        # Decide la modalità: LABELS (Testo token) o TICKS (Indici numerici)
        current_mode = "LABELS" if visible_x_range <= self.max_labels_threshold else "TICKS"
        
        # Piccola ottimizzazione: se la modalità non cambia, non ricalcolare le etichette
        last_mode = getattr(ax, '_last_label_mode', None)
        if current_mode == "TICKS" and last_mode == "TICKS": pass 
        ax._last_label_mode = current_mode

        # Calcola gli indici visibili interi
        idx_start = max(0, int(min(new_x_start, new_x_end)))
        idx_end = min(N, int(max(new_x_start, new_x_end)) + 1)
        idy_start = max(0, int(min(new_y_start, new_y_end)))
        idy_end = min(N, int(max(new_y_start, new_y_end)) + 1)

        if current_mode == "LABELS":
            # Mostra i NOMI dei token
            x_ticks = np.arange(idx_start, idx_end)
            x_ticks = x_ticks[x_ticks < N]
            y_ticks = np.arange(idy_start, idy_end)
            y_ticks = y_ticks[y_ticks < N]

            if len(x_ticks) > 0:
                labels_x = [self.current_tokens[i] for i in x_ticks]
                ax.set_xticks(x_ticks)
                # Rotazione 45° per leggere meglio i token lunghi
                ax.set_xticklabels(labels_x, rotation=45, ha='right', rotation_mode='anchor', fontsize=8, color='#aaaaaa')
                
                labels_y = [self.current_tokens[i] for i in y_ticks]
                ax.set_yticks(y_ticks)
                ax.set_yticklabels(labels_y, fontsize=8, color='#aaaaaa')
        else:
            # Mostra INDICI numerici
            step = max(5, int(visible_x_range // 10)) # Calcola uno step dinamico per non affollare
            ticks = np.arange(0, N, step)
            ax.set_xticks(ticks)
            ax.set_xticklabels(ticks, rotation=0, fontsize=8, color='#666')
            ax.set_yticks(ticks)
            ax.set_yticklabels(ticks, fontsize=8, color='#666')

    def _on_mouse_hover(self, event):
        """
        Gestisce il Tooltip al passaggio del mouse.
        """
        # Se siamo fuori dagli assi o il grafico non è pronto
        if event.inaxes != self.canvas.axes or self.im_ref is None:
            self.lbl_status.setText("Hover over the heatmap to see details")
            return
            
        # Arrotondamento per trovare l'indice del token
        x_idx = int(event.xdata + 0.5)
        y_idx = int(event.ydata + 0.5)
        
        # Controllo limiti (evita crash se il mouse è sul bordo estremo)
        if x_idx < 0 or x_idx >= len(self.current_tokens) or y_idx < 0 or y_idx >= len(self.current_tokens):
            return
        
        # Recupero info
        token_y = self.current_tokens[y_idx]
        token_x = self.current_tokens[x_idx]
        
        # Importante: mostriamo il valore REALE (raw), non quello alterato dal Gamma
        real_val = self.current_raw_matrix[y_idx, x_idx] if self.current_raw_matrix is not None else 0.0
        
        # Aggiornamento UI
        self.lbl_status.setText(f"{token_y} -> {token_x} | Val: {real_val:.4f}")