import numpy as np
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QSplitter, 
                             QGraphicsScene, QGraphicsPathItem, 
                             QGraphicsTextItem, QGraphicsRectItem,
                             QSpinBox, QComboBox) 
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import (QPen, QBrush, QColor, QFont,QPainterPath, QFontMetrics,QIcon)

from .ui.token_attention_workboard import ZoomableGraphicsView
from src.config import settings

class TokenAttentionView(QWidget):
    """
    Vista principale per la visualizzazione in forma di grafo delle attention dei singoli token.
    
    Responsabilità:
    - Coordinare i dati (Tensori) con la visualizzazione.
    - Gestire l'interattività e (Zoom, Pan, Hover, Click).
    - Aggiornare la grafica in risposta ai comandi della Toolbar (Head/k).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.attention_tensors = [] 
        self.tokens = []
        self.k = settings.K_VALUE if hasattr(settings, 'K_VALUE') else 5
        
        # Layout principale Verticale: Toolbar sopra, Splitter sotto
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # --- TOP TOOLBAR (Head Selector + K Selector) ---
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(10, 5, 5, 0)
        
        # Selettore Matrice (Head)
        lbl_layer = QLabel("HEAD:")
        lbl_layer.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))
        toolbar_layout.addWidget(lbl_layer)

        self.head_combo = QComboBox()
        self.head_combo.setStyleSheet(settings.get_stylesheet("QComboBox_style.qss"))
        self.head_combo.currentIndexChanged.connect(self.on_layer_changed)
        toolbar_layout.addWidget(self.head_combo)

        # Spaziatore
        toolbar_layout.addSpacing(10)

        # Selettore K
        lbl_k = QLabel("Top-K:")
        lbl_k.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))
        toolbar_layout.addWidget(lbl_k)

        self.spin_k = QSpinBox() 
        min_k = settings.MIN_K_VALUE if hasattr(settings, 'MIN_K_VALUE') else 1
        max_k = settings.MAX_K_VALUE if hasattr(settings, 'MAX_K_VALUE') else 15
        self.spin_k.setRange(min_k, max_k)
        self.spin_k.setValue(self.k)
        self.spin_k.setStyleSheet(settings.get_stylesheet("QSpinBox_style.qss"))
        self.spin_k.valueChanged.connect(self.on_k_changed)
        toolbar_layout.addWidget(self.spin_k)

        # Stretch finale per spingere tutto a sinistra
        toolbar_layout.addStretch()

        # Aggiungo la toolbar al layout principale
        main_layout.addLayout(toolbar_layout)

        # --- AREA CENTRALE (Splitter: Lista + Grafo) ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(5)
        self.splitter.setStyleSheet(settings.get_stylesheet("QSplitter_style.qss"))
        main_layout.addWidget(self.splitter)

        # --- SEZIONE SINISTRA (Lista Tokens) ---
        self.left_widget = QWidget()
        self.left_widget.setMaximumWidth(250)
        left_layout = QVBoxLayout(self.left_widget)
        left_layout.setContentsMargins(10, 10, 0, 10) # Un po' di margine
        
        lbl_list = QLabel("Token list")
        lbl_list.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))
        left_layout.addWidget(lbl_list)
        
        self.token_list = QListWidget()
        self.token_list.setStyleSheet(settings.get_stylesheets("QList_style.qss","QScrollBar_style.qss"))
        self.token_list.itemClicked.connect(self.on_token_clicked)
        left_layout.addWidget(self.token_list)
        
        self.splitter.addWidget(self.left_widget)

        # --- SEZIONE DESTRA (Grafo) ---
        self.right_widget = QWidget()
        right_layout = QVBoxLayout(self.right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scene = QGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene)
        
        self.placeholder_label = QLabel("Select a token")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))
        
        right_layout.addWidget(self.placeholder_label)
        right_layout.addWidget(self.view)
        self.view.hide()
        
        self.splitter.addWidget(self.right_widget)
        self.splitter.setSizes([200, 650])

    def update_data(self, attention_tensors,tokens, k=None):
        """
        Aggiorna i dati.
        attention_tensors: List[np.ndarray] -> Lista di matrici di attenzione
        tokens: List[str] -> Lista dei token
        """
        # Se viene passato un singolo tensore per sbaglio, lo mettiamo in una lista
        if not isinstance(attention_tensors, list):
            self.attention_tensors = [np.array(attention_tensors)]
        else:
            self.attention_tensors = [np.array(t) for t in attention_tensors]

        self.tokens = tokens
        
        # Aggiornamento K se necessario
        if k is not None:
            self.k = k
            self.spin_k.blockSignals(True)
            self.spin_k.setValue(self.k)
            self.spin_k.blockSignals(False)
        
        # Popolamento Head Combo Box
        self.head_combo.blockSignals(True)
        self.head_combo.clear()
                
        icon_path = "assets/attention_navigator/item_icons/head.svg" 
        icon = QIcon(icon_path)
        
        if self.attention_tensors:
            for i in range(len(self.attention_tensors)):
                self.head_combo.addItem(icon,f"Head {i}")
            self.head_combo.setCurrentIndex(0)
        self.head_combo.blockSignals(False)

        # Popolamento Lista Token
        self.token_list.clear()
        self.scene.clear()
        self.view.hide()
        self.placeholder_label.show()
        self.placeholder_label.setText(f"Data loaded. Select a token")

        # Usiamo la lunghezza del primo tensore
        if self.attention_tensors and len(self.attention_tensors) > 0:
            first_tensor = self.attention_tensors[0]
            num_tokens = first_tensor.shape[0]
            
            for i in range(num_tokens):
                txt = f"{i}) {tokens[i]}" if i < len(tokens) else f"Token_{i}"
                self.token_list.addItem(txt)

    def get_current_attention_matrix(self):
        """Helper per recuperare la matrice selezionata nel combo box."""
        idx = self.head_combo.currentIndex()
        if 0 <= idx < len(self.attention_tensors):
            return self.attention_tensors[idx]
        return None

    def on_layer_changed(self, index):
        """Callback quando si cambia la matrice/layer dal ComboBox."""
        current_item = self.token_list.currentItem()
        if current_item:
            row = self.token_list.row(current_item)
            self.draw_graph(row, current_item.text())

    def on_k_changed(self, k_value):
        """Recepisce il cambio di valore k e agisce di conseguenza aggiornando la vista"""
        try:
            self.k = k_value
            current_item = self.token_list.currentItem()
            if current_item:
                row = self.token_list.row(current_item)
                self.draw_graph(row, current_item.text())
        except ValueError:
            pass 

    def on_token_clicked(self, item):
        """Recepisce il click del token e agisce di conseguenza presentando l'informazione associata"""
        if not self.attention_tensors:
            return
        row = self.token_list.row(item)
        self.placeholder_label.hide()
        self.view.show()
        self.draw_graph(row, item.text())
        
    def draw_graph(self, source_index, source_name: str):
        """
        Pulisce la scena e ridisegna il grafo di attenzione per il token sorgente selezionato.

        Logica di rendering:
        1. **Recupero Dati**: Ottiene la riga di attenzione e calcola i Top-K target.
        2. **Layout**: Posiziona il nodo sorgente a sinistra e i target a destra in colonna.
        3. **Connessioni**: Disegna linee pesate tra sorgente e target.
        """
        self.scene.clear()
        
        # RECUPERO LA MATRICE CORRENTE
        # Ottiene la matrice (Head) attualmente selezionata nel menu
        attention_matrix = self.get_current_attention_matrix()
        if attention_matrix is None:
            return

        attention_row = attention_matrix[source_index]
        
        # Ordina gli indici per peso decrescente e crea la maschera di filtraggio
        # (Maschera causale: solo token precedenti + Soglia minima di rumore 0.001)
        sorted_indices = np.argsort(attention_row)[::-1]
        mask = (sorted_indices <= source_index) & (attention_row[sorted_indices] > 0.001)

        # Seleziona solo i primi K indici che soddisfano la maschera
        top_indices = sorted_indices[mask][:self.k]
        
        # Parametri geometrici per il layout del grafo
        start_x, start_y = 0, 0 
        target_x_offset = 250     
        target_spacing_y = 50     
        padding = 10              
        
        font = QFont("Monaco", 11)
        
        # Crea il nodo principale a sinistra ed estrae il punto di ancoraggio destro
        source_rect = self._add_rounded_node(start_x, start_y, source_name, 
                                             QColor(59,34,95, 100), QColor("#6834b2"), 
                                             font, padding, is_source=True)
        
        source_out_pt = QPointF(source_rect.right()+2, source_rect.center().y())

        total_height = len(top_indices) * target_spacing_y
        current_y = start_y - (total_height / 2) + (target_spacing_y / 2)

        # Evidenzia visivamente i token target nella lista laterale
        self.highlight_indices(top_indices)

        # Target e Connessioni
        for _, target_idx in enumerate(top_indices):
            weight = attention_row[target_idx]
            
            # Recupera il testo del token (gestione fallback se indice fuori range)
            txt_token = self.tokens[target_idx] if target_idx < len(self.tokens) else str(target_idx)
            target_name = f"{target_idx}) {txt_token}"
            
            # Crea il nodo target a destra
            target_rect = self._add_rounded_node(target_x_offset, current_y, target_name,
                                                QColor(39, 174, 96, 100), QColor("#2ECC71"), 
                                                font, padding)
            
            target_in_pt = QPointF(target_rect.left(), target_rect.center().y())
            
            # Disegna la freccia di collegamento
            self._add_squared_arrow(source_out_pt, target_in_pt, weight)
            current_y += target_spacing_y

        self.view.setSceneRect(self.scene.itemsBoundingRect().adjusted(-50, -50, 50, 50))

    def _add_rounded_node(self, x, y, text, fill_color, border_color, font, padding, is_source=False):
        """
        Crea un nodo grafico rettangolare con bordi arrotondati e lo aggiunge alla scena.

        Args:
            x, y: Coordinate di riferimento per il posizionamento.
            text: Testo da visualizzare nel nodo.
            is_source (bool): Se True, centra il nodo su X. Se False, allinea a sinistra.
        
        Returns:
            QRectF: Il rettangolo geometrico che delimita il nodo creato.
        """
        # Calcola le dimensioni del testo per adattare il box
        fm = QFontMetrics(font)
        text_w = fm.horizontalAdvance(text)
        text_h = fm.height()
        
        box_w = text_w + (padding * 2)
        box_h = text_h + (padding * 2)
        
        # Calcola la posizione top-left in base all'allineamento richiesto
        top_left_x = x - (box_w / 2) if is_source else x 
        top_left_y = y - (box_h / 2)
        
        rect = QRectF(top_left_x, top_left_y, box_w, box_h)
        
        # Disegna la forma arrotondata
        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8) 
        
        # Aggiunge il rettangolo colorato (Z=10)
        path_item = QGraphicsPathItem(path)
        path_item.setBrush(QBrush(fill_color))
        path_item.setPen(QPen(border_color, 2.0))
        path_item.setZValue(10)
        self.scene.addItem(path_item)
        
        # Aggiunge il testo sopra il rettangolo (Z=11)
        text_item = QGraphicsTextItem(text)
        text_item.setFont(font)
        text_item.setDefaultTextColor(QColor("#FFFFFF"))
        text_item.setPos(top_left_x + padding, top_left_y + padding)
        text_item.setZValue(11)
        self.scene.addItem(text_item)
        
        return rect
    
    def highlight_indices(self, indices_to_highlight):
        """
        Aggiorna lo stile visivo della lista dei token laterale.
        
        Applica uno sfondo colorato (Highlight) agli elementi corrispondenti
        agli indici forniti e rimuove lo sfondo dagli altri.
        """
        highlight_color = QColor(46,204,113, 80)
        default_brush = QBrush(Qt.BrushStyle.NoBrush) 
        
        # Itera su tutte le righe della lista per impostare o resettare lo sfondo
        for row in range(self.token_list.count()):
            item = self.token_list.item(row)
            if row in indices_to_highlight:
                item.setBackground(QBrush(highlight_color))
            else:
                item.setBackground(default_brush)

    def _add_squared_arrow(self, start_pt, end_pt, weight):
        """
        Disegna una connessione a forma di freccia squadrata (percorso ortogonale).

        Caratteristiche visive basate sul peso (`weight`):
        1. **Spessore**: Aumenta proporzionalmente al peso.
        2. **Opacità**: Più opaco per pesi maggiori.
        3. **Label**: Mostra il valore numerico del peso su sfondo scuro.
        """
        path = QPainterPath()
        path.moveTo(start_pt)
        
        # Calcola il punto medio per creare la spezzata verticale
        mid_x = (start_pt.x() + end_pt.x()) / 2
        
        path.lineTo(mid_x, start_pt.y())        
        path.lineTo(mid_x, end_pt.y())          
        path.lineTo(end_pt.x(), end_pt.y())     
        
        line_item = QGraphicsPathItem(path)
        
        # Calcola stile dinamico basato sull'intensità dell'attenzione
        line_width = 1.0 + (weight * 6.0) 
        color = QColor(200, 200, 200) 
        color.setAlphaF(min(0.5 + weight, 1.0)) 
        
        pen = QPen(color, min(line_width, 4.0))
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        line_item.setPen(pen)
        line_item.setZValue(0) # Sotto i nodi
        self.scene.addItem(line_item)
    
        # Crea l'etichetta del valore numerico
        txt = QGraphicsTextItem(f"{weight:.3f}")
        font = QFont("Monaco", 9, QFont.Weight.Bold)
        txt.setFont(font)
        txt.setDefaultTextColor(QColor("#FFFFE0")) 
        
        text_rect = txt.boundingRect()
        
        # Posiziona l'etichetta al centro del segmento finale orizzontale
        segment_center_x = (mid_x + end_pt.x()) / 2
        txt_x = segment_center_x - (text_rect.width() / 2)
        txt_y = end_pt.y() - text_rect.height() - 5
        txt.setPos(txt_x, txt_y)
        
        bg_rect = QGraphicsRectItem(txt_x, txt_y, text_rect.width(), text_rect.height())
        bg_rect.setBrush(QBrush(QColor(0, 0, 0, 180))) 
        bg_rect.setZValue(1)
        txt.setZValue(2)
        
        self.scene.addItem(bg_rect)
        self.scene.addItem(txt)