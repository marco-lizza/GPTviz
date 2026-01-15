from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QAbstractItemView, QWidget, QVBoxLayout, QLabel
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon

from ..config import settings

class FileList(QTreeWidget):
    """
    Widget ad albero personalizzato per la visualizzazione gerarchica dei file.

    Estende `QTreeWidget` per mostrare una lista di file raggruppati per 'Dominio'.

    Signals:
        file_clicked (str): Emesso quando un utente clicca su un nodo 'file' (foglia).
            Il payload è il nome del file (es. "data.arrow").
    """
    
    file_clicked = pyqtSignal(str)    

    def __init__(self):
        """
        Inizializza il widget dell'albero file.

        """
        super().__init__()

        self.setHeaderHidden(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.setUniformRowHeights(True)
        
        stylesheet = settings.get_stylesheets("QTreeWidget_style.qss", "QScrollBar_style.qss")
        self.setStyleSheet(stylesheet)
        
        self.itemClicked.connect(self._on_file_clicked)

        # Abilito il tracciamento mouse. 
        self.setMouseTracking(True)

    def _on_file_clicked(self, item: QTreeWidgetItem, column: int):
        """
        Gestisce il click su un elemento dell'albero.

        Verifica se l'elemento cliccato è un file o una cartella controllando
        i metadati nascosti (`UserRole`). Se è un file, emette il segnale esterno.

        Args:
            item (QTreeWidgetItem): L'elemento cliccato.
            column (int): La colonna cliccata (qui è sempre 0).
        """
        # Recupera il tipo di item salvato nei metadati
        item_type = item.data(0, Qt.ItemDataRole.UserRole) 
        
        if item_type == "file":
            # Recupera il nome del file salvato nello slot successivo (UserRole + 1)
            filename = item.data(0, Qt.ItemDataRole.UserRole + 1)
            self.file_clicked.emit(filename)
    
    def update_sidebar(self, files: dict):
        """
        Rigenera l'intera struttura dell'albero in base al dizionario fornito.

        Pulisce la vista corrente e crea nuovi nodi per ogni dominio e file.

        Args:
            files (dict): Dizionario nella forma `{ "DominioA": ["file1", "file2"], ... }`.
        """
        self.clear()
        for domain, names_list in files.items():
            self.add_files_of_a_domain(domain, names_list)

    def add_files_of_a_domain(self, domain: str, names_list: list):
        """
        Crea un nodo genitore (Directory) e i suoi figli (Files).

        Struttura Dati `QTreeWidgetItem`:
        * **DisplayRole (Text)**: Nome visualizzato.
        * **UserRole**: Tipo di nodo ("dir" o "file").
        * **UserRole + 1**: Dati extra (solo per i file: il nome file reale).

        Args:
            domain (str): Il nome del raggruppamento (cartella virtuale).
            names_list (list): Lista di stringhe con i nomi dei file.
        """
        # Creazione Nodo Cartella
        dir_item = QTreeWidgetItem(self)
        dir_item.setText(0, domain)
        dir_item.setIcon(0, QIcon(settings.get_asset_path("file_icons/directory.svg")))
        dir_item.setData(0, Qt.ItemDataRole.UserRole, "dir")

        # Creazione Nodi File
        for name in names_list:
            file_item = QTreeWidgetItem(dir_item)
            file_item.setText(0, name)
            
            # Metadata: Tipo
            file_item.setData(0, Qt.ItemDataRole.UserRole, "file")
            # Metadata: Valore (Nome file utile per il caricamento)
            file_item.setData(0, Qt.ItemDataRole.UserRole + 1, name)
            
            file_item.setIcon(0, QIcon(settings.get_asset_path("file_icons/arrow.svg")))

    def mouseMoveEvent(self, event):
        """
        Gestisce l'evento di movimento del mouse per il feedback visivo (Cursore).

        Cambia il cursore in 'PointingHand' (manina) solo se si passa sopra
        un elemento foglia (file).

        Args:
            event (QMouseEvent): L'evento generato dal movimento del mouse.
        """
        item = self.itemAt(event.pos())

        if item and item.childCount() == 0:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        super().mouseMoveEvent(event)


class SidebarView(QWidget):
    """
    Container per la barra laterale (Sidebar).

    Avvolge la `FileList` aggiungendo un titolo ("EXPLORER") e gestendo
    il layout e le dimensioni massime/minime del pannello laterale.

    """

    def __init__(self):
        super().__init__()
        
        self.setStyleSheet("SidebarView { min-width: 200px; max-width: 250px; }")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.title_label = QLabel("EXPLORER")
        stylesheet = settings.get_stylesheet("QLabel_style.qss")
        self.title_label.setStyleSheet(stylesheet)
        
        self.file_list = FileList()

        layout.addWidget(self.title_label)
        layout.addWidget(self.file_list)