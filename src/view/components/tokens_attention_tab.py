import numpy as np
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QSplitter, QGraphicsView, 
                             QGraphicsScene, QGraphicsRectItem, 
                             QGraphicsLineItem, QGraphicsTextItem)
from PyQt6.QtCore import Qt,pyqtSignal
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPainter

from src.config import settings

# --- Classe di supporto per rendere il grafo zoomabile e trascinabile ---
class ZoomableGraphicsView(QGraphicsView):
    """
    Estensione di QGraphicsView che abilita l'interazione avanzata (Zoom & Pan).

    Permette all'utente di navigare nel grafo generato usando:
    1. **Rotellina del mouse**: Per zoomare avanti/indietro.
    2. **Click e trascinamento (Drag)**: Per spostarsi nella scena (Panning).
    
    Attiva automaticamente l'Antialiasing per linee e cerchi più morbidi.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def wheelEvent(self, event):
        """
        Gestisce lo zoom centrato sulla posizione del mouse.
        """
        # Gestione dello zoom con la rotellina
        zoom_in_factor = settings.ZOOM_FACTOR
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)


class TokenAttentionView(QWidget):
    """
    Vista analitica per esplorare le relazioni 'Uno-a-Molti' tra i token.
    
    Layout:
        - **Sinistra (Lista)**: Elenco di tutti i token disponibili.
        - **Destra (Grafo)**: Visualizzazione a nodi con collegamenti pesati.

    Attributes:
        attention_tensor (np.array): La matrice di attenzione caricata (NxN).
        k (int): Numero di connessioni più forti da visualizzare (Top-K).
        scene (QGraphicsScene): Il contenitore degli oggetti grafici (nodi, linee).
    """

    def __init__(self, parent=None):
        """Inizializza l'interfaccia divisa (Splitter) e la scena grafica."""
        super().__init__(parent)
        
        self.attention_tensor = None
        self.k = 0
        
        main_layout = QHBoxLayout(self)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        # --- SEZIONE SINISTRA: Lista dei Token ---
        self.left_widget = QWidget()
        left_layout = QVBoxLayout(self.left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_list = QLabel("Lista Token")
        lbl_list.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(lbl_list)
        
        self.token_list = QListWidget()
        self.token_list.itemClicked.connect(self.on_token_clicked)
        left_layout.addWidget(self.token_list)
        
        self.splitter.addWidget(self.left_widget)

        # --- SEZIONE DESTRA: Visualizzazione Grafo ---
        self.right_widget = QWidget()
        right_layout = QVBoxLayout(self.right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scene = QGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene)
        
        # Placeholder visibile quando nessun token è selezionato
        self.placeholder_label = QLabel("Seleziona un token dalla lista")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("color: #888; font-style: italic; font-size: 14px;")
        
        right_layout.addWidget(self.placeholder_label)
        right_layout.addWidget(self.view)
        
        self.view.hide() # Nascosto inizialmente
        
        self.splitter.addWidget(self.right_widget)
        
        self.splitter.setSizes([200, 600])

    def update_data(self, attention_tensor, tokens, k=settings.K_VALUE):
        """
        Carica nuovi dati e rigenera la lista dei token.

        """
        self.attention_tensor = np.array(attention_tensor)
        self.k = k
        
        self.tokens=tokens
        self.token_list.clear()
        self.scene.clear()
        self.view.hide()
        self.placeholder_label.show()
        self.placeholder_label.setText(f"Dati caricati. Seleziona un token (Top-{k})")

        if self.attention_tensor is not None:
            num_tokens = self.attention_tensor.shape[0]
            for i in range(num_tokens):
                self.token_list.addItem(tokens[i])

    def on_token_clicked(self, item):
        """
        Callback invocato al click su un elemento della lista.
        
        Avvia il disegno del grafo.
        """
        if self.attention_tensor is None:
            return

        row = self.token_list.row(item)

        self.placeholder_label.hide()
        self.view.show()
    
        self.draw_graph(row,item.text())

    def draw_graph(self,source_index,source_name: str):
        """
        Costruisce e disegna il grafo 'Source-to-Targets'.

        Algoritmo di visualizzazione:
        1. Estrae la riga di attenzione corrispondente al `source_index`.
        2. Identifica i `k` indici con valore più alto (Top-K) usando `argsort`.
        3. Disegna il nodo sorgente a sinistra (Blu).
        4. Disegna i nodi target a destra (Verde), impilati verticalmente.
        5. Disegna linee di collegamento con spessore proporzionale al peso dell'attenzione.

        Args:
            source_index (int): L'indice del token selezionato nella lista.
        """
        self.scene.clear()
        
        # Recupero la riga di attenzione per il token selezionato
        attention_row = self.attention_tensor[source_index]
        
        # Troviamo i Top K (Gestisco anche il caso in cui ci sono meno token di K)
        num_tokens = len(attention_row)
        effective_k = min(self.k, num_tokens)
        
        # argsort restituisce indici crescenti, prendiamo gli ultimi k e invertiamo
        top_indices = np.argsort(attention_row)[-effective_k:][::-1]
        
        # Parametri geometrici
        center_x, center_y = 0, 0  # Posizione sorgente
        target_x_offset = 300      # Distanza target
        target_spacing_y = 80      # Spaziatura verticale target
        node_radius = 25
        
        # Disegno Token Sorgente (Blu)
        source_color = QColor("#3498db")
        self._add_node(center_x, center_y, node_radius,source_name, source_color, is_source=True)

        # Calcolo posizione verticale iniziale per centrare i target rispetto alla sorgente
        start_y = -((effective_k - 1) * target_spacing_y) / 2
        
        # Ciclo di disegno Target e Archi
        for i, target_idx in enumerate(top_indices):
            weight = attention_row[target_idx]
            target_y = start_y + (i * target_spacing_y)
            
            target_color = QColor("#2ecc71") # Verde
            
            # Disegno la linea di connessione 
            line_pen = QPen(Qt.GlobalColor.gray)
            line_width = 1 + (weight * 10)
            line_pen.setWidthF(min(line_width, 5.0))
            
            line = QGraphicsLineItem(center_x + node_radius, center_y, 
                                     target_x_offset - node_radius, target_y)
            line.setPen(line_pen)
            self.scene.addItem(line)
            
            # Aggiungo etichetta numerica del peso sulla linea
            weight_text = QGraphicsTextItem(f"{weight:.2f}")
            weight_text.setFont(QFont("Arial", 8))
            # Posiziono il testo a metà strada
            weight_text.setPos(center_x + (target_x_offset/2) - 10, (center_y + target_y)/2 - 10)
            self.scene.addItem(weight_text)

            # Disegno nodo target
            self._add_node(target_x_offset, target_y, node_radius, self.tokens[target_idx], target_color)

        # Resetta la vista per inquadrare tutti gli oggetti creati
        self.view.setSceneRect(self.scene.itemsBoundingRect())

    def _add_node(self, x, y, r, text, color, is_source=False):
        """
        Helper method per disegnare un nodo (cerchio + testo + etichetta).

        Crea un `QGraphicsEllipseItem` per il cerchio e `QGraphicsTextItem`
        per il contenuto testuale, aggiungendoli alla scena corrente.
        """
        # Cerchio colorato
        ellipse = QGraphicsRectItem(x - r, y - r, r * 2, r * 2)
        ellipse.setBrush(QBrush(color))
        ellipse.setPen(QPen(Qt.GlobalColor.black))
        
        self.scene.addItem(ellipse)
        
        # Testo centrale (Indice Token)
        text_item = QGraphicsTextItem(text)
        font = QFont("Arial", 10, QFont.Weight.Bold)
        text_item.setFont(font)
        
        # Centratura testo nel cerchio
        text_rect = text_item.boundingRect()
        text_item.setPos(x - text_rect.width() / 2, y - text_rect.height() / 2)
        
        self.scene.addItem(text_item)
        
        # Etichetta descrittiva sotto il nodo (Source/Target)
        desc = "Source" if is_source else "Target"
        desc_item = QGraphicsTextItem(desc)
        desc_item.setFont(QFont("Arial", 8))
        desc_rect = desc_item.boundingRect()
        desc_item.setPos(x - desc_rect.width() / 2, y + r + 5)
        self.scene.addItem(desc_item)