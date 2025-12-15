from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        plt.style.use('dark_background') 
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig.patch.set_facecolor('#333333')
        self.axes.set_facecolor('#333333')
        super().__init__(self.fig)

class WorkspaceView(QFrame):
    def __init__(self):
        super().__init__()
        
        self.setStyleSheet("background-color: #333333;")
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        
        self.current_widget = None
        self.reset_view()

    def reset_view(self):
        self._clear_content() # Rimuove grafico o label precedente
        
        label = QLabel("Nessuna head selezionata")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #666; font-size: 24px; font-weight: bold;")
        
        self.layout.addWidget(label)
        self.current_widget = label

    def visualize_attentions_matrix(self, attention_tensor):
        """
        Visualizza la matrice (o il grafico).
        """
        if attention_tensor is None:
            return

        self._clear_content()
        matrix_np = attention_tensor.detach().cpu().squeeze().numpy()

        canvas = MplCanvas(self, width=5, height=4, dpi=100)
        
        # Disegno Heatmap
        im = canvas.axes.imshow(matrix_np, aspect='auto', cmap='viridis', interpolation='nearest')
        canvas.fig.colorbar(im, ax=canvas.axes)
        
        # Styling assi
        canvas.axes.set_title("Attention Head Heatmap", color='white')
        canvas.axes.tick_params(colors='#aaaaaa')

        # Aggiunta al layout
        self.layout.addWidget(canvas)
        self.current_widget = canvas

    def _clear_content(self):
        """
        Rimuove SOLO il widget contenuto nel layout, senza distruggere il layout stesso.
        """
        if self.current_widget is not None:
            self.layout.removeWidget(self.current_widget)
            self.current_widget.deleteLater() # Cancella dalla memoria
            self.current_widget = None