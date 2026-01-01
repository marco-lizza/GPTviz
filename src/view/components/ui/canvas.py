# src/ui/canvas.py
import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
matplotlib.use('QtAgg')

class MplCanvas(FigureCanvas):
    """
    Widget personalizzato che integra una figura Matplotlib all'interno di un'interfaccia PyQt6.
    """

    def __init__(self, parent=None, width=5, height=5, dpi=100):
        """
        Inizializza il canvas, la figura e gli assi.

        Args:
            parent (QWidget, optional): Il widget genitore Qt. Default è None.
            width (int): Larghezza della figura in pollici. Default è 5.
            height (int): Altezza della figura in pollici. Default è 5.
            dpi (int): Risoluzione in punti per pollice. Default è 100.
        """
        # Configurazione Figura
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        # Tema Scuro
        self.fig.patch.set_facecolor('#2b2b2b')
        self.axes.set_facecolor('#2b2b2b')
        
        # Margini iniziali
        self.fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9)
        
        super().__init__(self.fig)