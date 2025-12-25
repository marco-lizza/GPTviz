from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QTextCursor
from src.config import settings

class ConsoleView(QTextEdit):
    """
    Widget personalizzato per la visualizzazione dei log di sistema.

    `QTextEdit` configurato in modalità sola lettura (ReadOnly).
    Include un parser leggero che traduce tag personalizzati in codice HTML,
    permettendo al Modello di inviare messaggi semantici (es. "errore", "successo")
    senza doversi preoccupare dei codici colore esadecimali, che sono gestiti qui
    tramite le impostazioni globali.

    Supported Tags:
        * `<erro>...</erro>`: Rosso grassetto (Errori critici).
        * `<succ>...</succ>`: Verde (Operazioni completate).
        * `<warn>...</warn>`: Arancione (Avvisi).
        * `<info>...</info>`: Ciano (Informazioni tecniche).
        * `<gene>...</gene>`: Viola grassetto (Highlight generici).
    """

    def __init__(self):
        """
        Inizializza la console, applica lo stile e costruisce la mappa dei tag.
        """
        super().__init__()

        # Applica lo stile CSS specifico per l'area di testo e la scrollbar
        stylesheet = settings.get_stylesheets("QTextEdit_style.qss", "QScrollBar_style.qss")
        self.setStyleSheet(stylesheet)
        
        # Impedisce all'utente di scrivere nella console
        self.setReadOnly(True)

        # Mappa di traduzione: Tag Custom -> HTML con stili CSS inline.
        # I colori vengono letti dinamicamente da settings.CONSOLE_PALETTE.
        self.tag_map = {
            # Errori (Rosso)
            "<erro>": f"<span style='color: {settings.CONSOLE_PALETTE['ERRO_COLOR']}; font-weight: bold;'>(erro) ",
            "</erro>": "</span>",
            
            # Successo (Verde)
            "<succ>": f"<span style='color: {settings.CONSOLE_PALETTE['SUCC_COLOR']};'>(succ) ",
            "</succ>": "</span>",
            
            # Warning (Arancio)
            "<warn>": f"<span style='color: {settings.CONSOLE_PALETTE['WARN_COLOR']};'>(warn) ",
            "</warn>": "</span>",
            
            # Info / Highlight (Ciano)
            "<info>": f"<span style='color: {settings.CONSOLE_PALETTE['INFO_COLOR']};'>(info) ",
            "</info>": "</span>",
            
            # Evidenziato generico (Viola)
            "<gene>": f"<span style='color: {settings.CONSOLE_PALETTE['GENE_COLOR']}; font-weight: bold;'>(gene) ",
            "</gene>": "</span>"
        }

    def append_log(self, text: str):
        """
        Processa il testo in ingresso, applica la formattazione e lo accoda alla vista.

        Args:
            text (str): La stringa di log contenente opzionalmente i tag custom.
        """
        formatted_text = text

        # Sostituzione dei tag
        for tag, html_val in self.tag_map.items():
            formatted_text = formatted_text.replace(tag, html_val)
        
        # Gestione a capo HTML
        formatted_text = formatted_text.replace("\n", "<br>")

        final_html = f"<span style='color: #666666;'>>></span> {formatted_text}"

        self.append(final_html)
        
        # Porta sempre la vista all'ultima riga per mostrare il messaggio più recente
        self.ensure_cursor_at_end()

    def ensure_cursor_at_end(self):
        """
        Forza lo scorrimento (scroll) della vista fino all'ultima riga.
        
        Utilizza `QTextCursor` per spostare il punto di inserimento alla fine
        del documento, costringendo il widget a scorrere visivamente.
        """
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)

    def clear_console(self):
        """
        Rimuove tutto il testo presente nella console.
        """
        self.clear()