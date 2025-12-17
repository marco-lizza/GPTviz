from PyQt6.QtWidgets import QWidget, QVBoxLayout
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class MplCanvas(FigureCanvas):
    """Classe di utilità per integrare Matplotlib in PyQt6"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        plt.style.use('dark_background') 
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig.patch.set_facecolor('#333333')
        self.axes.set_facecolor('#333333')
        super().__init__(self.fig)

class AttentionHeatmapView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.current_canvas = None

    def update_data(self, attention_tensor):
        """Riceve il tensore e ridisegna il grafico"""
        
        # Pulisce il grafico precedente per liberare memoria
        if self.current_canvas is not None:
            self.layout.removeWidget(self.current_canvas)
            self.current_canvas.deleteLater()
            self.current_canvas = None

        if attention_tensor is None:
            return

        matrix_np = attention_tensor.detach().cpu().squeeze().numpy()

        self.current_canvas = MplCanvas(self, width=5, height=4, dpi=100)
        
        # Disegno Heatmap
        im = self.current_canvas.axes.imshow(matrix_np, aspect='auto', cmap='viridis', interpolation='nearest')
        self.current_canvas.fig.colorbar(im, ax=self.current_canvas.axes)
        
        self.current_canvas.axes.set_title("Attention Head Heatmap", color='white')
        self.current_canvas.axes.tick_params(colors='#aaaaaa', labelcolor='#aaaaaa')
        
        self.current_canvas.setStyleSheet("background-color: #333333; border: none;")

        self.layout.addWidget(self.current_canvas)