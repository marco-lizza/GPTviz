import matplotlib

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
matplotlib.use('QtAgg')

class MplCanvas(FigureCanvas):
    """
    Widget personalizzato che incapsula una figura Matplotlib.
    Eredita da FigureCanvasQTAgg, quindi si comporta come un QWidget standard
    (può essere aggiunto ai layout PyQt) ma contiene un grafico.
    """

    def __init__(self, parent=None, width=5, height=5, dpi=100):
        """
        Inizializza il canvas.

        Args:
            parent (QWidget): Il widget genitore (opzionale).
            width (float): Larghezza della figura in pollici (default 5).
            height (float): Altezza della figura in pollici (default 5).
            dpi (int): Risoluzione (Dots Per Inch), default 100.
        """
        
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        self.fig.patch.set_facecolor('#181818')
        
        self.fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9)

        super().__init__(self.fig)