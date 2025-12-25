from PyQt6.QtWidgets import QWidget, QVBoxLayout
import matplotlib
# Imposta il backend di Matplotlib per integrarsi con Qt
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np

class MplCanvas(FigureCanvas):
    """
    PROVVISORIA
    Canvas personalizzato per l'integrazione di Matplotlib all'interno di widget PyQt6.

    Attributes:
        fig (Figure): L'oggetto Figure di Matplotlib (il contenitore grafico).
        axes (Axes): L'oggetto Axes (l'area di disegno vera e propria).
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """
        Inizializza il canvas con uno stile scuro predefinito.

        Args:
            parent (QWidget, optional): Il widget genitore Qt.
            width (float): Larghezza della figura in pollici.
            height (float): Altezza della figura in pollici.
            dpi (int): Risoluzione (Dots Per Inch).
        """
        plt.style.use('dark_background') 
        
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        self.fig.patch.set_facecolor('#333333')
        self.axes.set_facecolor('#333333')
        
        super().__init__(self.fig)

class AttentionHeatmapView(QWidget):
    """
    IN SVILUPPO
    Widget dedicato alla visualizzazione grafica della matrice di attenzione (Heatmap).

    Attributes:
        layout (QVBoxLayout): Layout contenitore.
        current_canvas (MplCanvas): Riferimento all'istanza corrente del grafico.
            Viene ricreato ad ogni aggiornamento per pulire la memoria.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        # Rimuove i margini per massimizzare l'area di disegno
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.current_canvas = None

    def update_data(self, attention_tensor, gamma=1.0):
        """
        Elabora il tensore e disegna la Heatmap.

        Il processo di visualizzazione segue questi step matematici:
        1. **Conversione**: Da PyTorch Tensor a NumPy Array.
        2. **Correzione Gamma**: Applica una trasformazione non lineare $V_{out} = V_{in}^\gamma$.
           * $\gamma > 1$: Aumenta il contrasto (evidenzia i picchi, sopprime il rumore).
           * $\gamma < 1$: Diminuisce il contrasto (rende visibili le connessioni deboli).

        Args:
            attention_tensor (torch.Tensor): Il tensore 2D contenente i pesi di attenzione.
            gamma (float): Il coefficiente di correzione esponenziale. Default 1.0 (lineare).
        """
        # Pulizia memoria: distrugge il widget Matplotlib precedente
        if self.current_canvas is not None:
            self.layout.removeWidget(self.current_canvas)
            self.current_canvas.deleteLater()
            self.current_canvas = None

        if attention_tensor is None:
            return

        # Creazione nuovo canvas
        self.current_canvas = MplCanvas(self, width=5, height=4, dpi=100)
        ax = self.current_canvas.axes
        fig = self.current_canvas.fig

        # 1. Convertiamo in numpy (rimuove gradienti e dimensioni extra)
        matrix_np = attention_tensor.detach().cpu().squeeze().numpy()

        # 2. Applicazione Gamma (Contrasto Dinamico)
        matrix_processed = np.power(matrix_np, gamma)

        im = ax.imshow(
            matrix_processed, 
            aspect='auto', 
            cmap='magma', 
            interpolation='nearest',
            vmin=0, 
            vmax=1
        )
        
        # Configurazione Colorbar
        cbar = fig.colorbar(im, ax=ax)
        cbar.outline.set_visible(False)
        cbar.ax.tick_params(labelsize=8, colors='#888888')
        
        # Configurazione Titolo Dinamico
        title_suffix = f" (Gamma: {gamma})" if gamma != 1.0 else ""
        ax.set_title(f"Attention Heatmap{title_suffix}", color='white', pad=20, fontsize=14, fontweight='bold')
        
        # Styling Assi
        ax.tick_params(colors='#666666', labelsize=9)
        
        # Pulizia visiva (rimuove il bordo quadrato del grafico)
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Aggiunta alla UI
        self.layout.addWidget(self.current_canvas)