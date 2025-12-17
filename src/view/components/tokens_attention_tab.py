import sys
import numpy as np
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QSplitter, QGraphicsView, 
                             QGraphicsScene, QGraphicsEllipseItem, 
                             QGraphicsLineItem, QGraphicsTextItem)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPainter

# --- Classe di supporto per rendere il grafo zoomabile e trascinabile ---
class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def wheelEvent(self, event):
        # Gestione dello zoom con la rotellina
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)

class TokenAttentionView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.attention_tensor = None
        self.k = 0
        
        main_layout = QHBoxLayout(self)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        # SEZIONE SINISTRA: Lista dei Token
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

        # SEZIONE DESTRA: Visualizzazione Grafo
        self.right_widget = QWidget()
        right_layout = QVBoxLayout(self.right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scene = QGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene)
        
        self.placeholder_label = QLabel("Seleziona un token dalla lista")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("color: #888; font-style: italic; font-size: 14px;")
        
        right_layout.addWidget(self.placeholder_label)
        right_layout.addWidget(self.view)
        
        self.view.hide()
        
        self.splitter.addWidget(self.right_widget)
        
        # Impostiamo una dimensione iniziale (es. 30% lista, 70% grafo)
        self.splitter.setSizes([200, 600])

    def update_data(self, attention_tensor, k=10):
        """
        Aggiorna la vista con una nuova matrice di attenzione e il parametro k.
        attention_tensor: numpy array o lista di liste (N x N)
        k: intero, quanti top-token mostrare
        """
        self.attention_tensor = np.array(attention_tensor)
        self.k = k
        
        self.token_list.clear()
        self.scene.clear()
        self.view.hide()
        self.placeholder_label.show()
        self.placeholder_label.setText(f"Dati caricati. Seleziona un token (Top-{k})")

        # PARTE DA AGGIORNARE CON NOMI CORRETTI DEI TOKEN 
        if self.attention_tensor is not None:
            num_tokens = self.attention_tensor.shape[0]
            for i in range(num_tokens):
                self.token_list.addItem(f"Token {i}")

    def on_token_clicked(self, item):
        """Gestisce il click su un token della lista"""
        if self.attention_tensor is None:
            return

        row = self.token_list.row(item)
        
        self.placeholder_label.hide()
        self.view.show()
        
        self.draw_graph(source_index=row)

    def draw_graph(self, source_index):
        """Disegna il grafo: Token Sorgente -> Linee -> Top K Token Target"""
        self.scene.clear()
        
        # Recupero la riga di attenzione per il token selezionato
        attention_row = self.attention_tensor[source_index]
        
        # Troviamo i Top K 
        num_tokens = len(attention_row)
        effective_k = min(self.k, num_tokens)
        
        top_indices = np.argsort(attention_row)[-effective_k:][::-1]
        
        center_x, center_y = 0, 0  # Posizione del token sorgente
        target_x_offset = 300      # Distanza orizzontale dei target
        target_spacing_y = 80      # Distanza verticale tra i target
        node_radius = 25
        
        # Disegno Token Sorgente
        source_color = QColor("#3498db")
        self._add_node(center_x, center_y, node_radius, f"{source_index}", source_color, is_source=True)

        # Disegno Token Target e Linee
        start_y = -((effective_k - 1) * target_spacing_y) / 2
        
        for i, target_idx in enumerate(top_indices):
            weight = attention_row[target_idx]
            target_y = start_y + (i * target_spacing_y)
            
            target_color = QColor("#2ecc71") 
            
            # Disegno la linea di connessione (spessore basato sul peso)
            line_pen = QPen(Qt.GlobalColor.gray)
            line_width = 1 + (weight * 10)
            line_pen.setWidthF(min(line_width, 5.0))
            
            line = QGraphicsLineItem(center_x + node_radius, center_y, 
                                     target_x_offset - node_radius, target_y)
            line.setPen(line_pen)
            self.scene.addItem(line)
            
            # Aggiungo etichetta peso sulla linea
            weight_text = QGraphicsTextItem(f"{weight:.2f}")
            weight_text.setFont(QFont("Arial", 8))
            weight_text.setPos(center_x + (target_x_offset/2) - 10, (center_y + target_y)/2 - 10)
            self.scene.addItem(weight_text)

            # Disegno nodo target
            self._add_node(target_x_offset, target_y, node_radius, f"{target_idx}", target_color)

        # Resetta la vista per inquadrare tutto
        self.view.setSceneRect(self.scene.itemsBoundingRect())

    def _add_node(self, x, y, r, text, color, is_source=False):
        """Helper per disegnare un cerchio con testo"""
        ellipse = QGraphicsEllipseItem(x - r, y - r, r * 2, r * 2)
        ellipse.setBrush(QBrush(color))
        ellipse.setPen(QPen(Qt.GlobalColor.black))
        
        """ 
        Flag per rendere i nodi movibili singolarmente (opzionale)
        ellipse.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable)
        ellipse.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable)
        """
        self.scene.addItem(ellipse)
        
        # Testo dentro il nodo
        text_item = QGraphicsTextItem(text)
        font = QFont("Arial", 10, QFont.Weight.Bold)
        text_item.setFont(font)
        
        # Centrare il testo
        text_rect = text_item.boundingRect()
        text_item.setPos(x - text_rect.width() / 2, y - text_rect.height() / 2)
        
        self.scene.addItem(text_item)
        
        # Etichetta sotto il nodo per chiarire
        desc = "Source" if is_source else "Target"
        desc_item = QGraphicsTextItem(desc)
        desc_item.setFont(QFont("Arial", 8))
        desc_rect = desc_item.boundingRect()
        desc_item.setPos(x - desc_rect.width() / 2, y + r + 5)
        self.scene.addItem(desc_item)