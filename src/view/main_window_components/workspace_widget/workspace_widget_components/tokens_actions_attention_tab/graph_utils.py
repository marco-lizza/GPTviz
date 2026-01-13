from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsTextItem
from PyQt6.QtCore import Qt, QPointF,QRectF
from PyQt6.QtGui import QPen, QBrush, QColor, QPainterPath

from src.config import settings

class BaseNodeItem(QGraphicsPathItem):
    """Nodo grafico generico (usato sia per Azioni che per Token)."""
    def __init__(self, path, rect, text, fill_color, border_color, font, data_idx=None):
        super().__init__(path)
        self.setBrush(QBrush(fill_color))
        self.setPen(QPen(border_color, 2.0))
        self.setZValue(10)
        self.setAcceptHoverEvents(True)
        self.data_idx = data_idx
        
        self.text_item = QGraphicsTextItem(text, self)
        self.text_item.setFont(font)
        self.text_item.setDefaultTextColor(QColor("#FFFFFF"))
        txt_rect = self.text_item.boundingRect()
        self.text_item.setPos(rect.center().x() - txt_rect.width()/2, 
                              rect.center().y() - txt_rect.height()/2)

def draw_vertical_squared_link(scene, p1: QPointF, p2: QPointF, font, weight: float=None):
    """
    Disegna una linea squadrata dal BASSO verso l'ALTO.
    Include un badge (rettangolo colorato) per l'etichetta del peso.
    """
    # --- DISEGNO LINEA ---
    path = QPainterPath()
    path.moveTo(p1)
    
    mid_y = (p1.y() + p2.y()) / 2
    
    path.lineTo(p1.x(), mid_y)
    path.lineTo(p2.x(), mid_y)
    path.lineTo(p2.x(), p2.y())
    
    line_item = QGraphicsPathItem(path)
    
    # Stile Linea
    width = 1.0 + ((weight if weight else 1) * 5.0)
    base_color =QColor(settings.GRAPH_PALETTE["LINE"])
    
    # Calcola alpha (trasparenza) basata sul peso per la linea
    alpha_val = int(min(255, 100 + (weight if weight else 1) * 155))
    line_color = QColor(base_color)
    line_color.setAlpha(alpha_val)
    
    pen = QPen(line_color, width)
    pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
    line_item.setPen(pen)
    line_item.setZValue(-1) # La linea sta sullo sfondo
    scene.addItem(line_item)
    
    # --- CREAZIONE BADGE PESO ---

    if(weight):
        txt = QGraphicsTextItem(f"{weight:.3f}")
        txt.setFont(font)
        txt.setDefaultTextColor(QColor("#2c3e50")) 
        
        brect = txt.boundingRect()
        
        padding_x = 4
        padding_y = 0
        rect_w = brect.width() + (padding_x * 2)
        rect_h = brect.height() + (padding_y * 2)
        
        # Disegna il rettangolo di sfondo (Badge)
        badge_rect = QRectF(0, 0, rect_w, rect_h)
        badge_path = QPainterPath()
        badge_path.addRoundedRect(badge_rect, 4, 4) 
        
        badge_item = QGraphicsPathItem(badge_path)
        badge_item.setBrush(QBrush(base_color)) 
        badge_item.setPen(QPen(Qt.PenStyle.NoPen)) 
        badge_item.setZValue(0) 
        
        # Unisci Testo e Badge
        # Imposta il testo come "figlio" del rettangolo, così si muovono insieme
        txt.setParentItem(badge_item)
        txt.setPos(padding_x, padding_y) 
        
        # Posizionamento nella Scena
        final_x = p2.x() - (rect_w / 2)
        final_y = p2.y() + 5 
        
        badge_item.setPos(final_x, final_y)
        
        scene.addItem(badge_item)