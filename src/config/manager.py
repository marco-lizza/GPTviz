import os
import json
from .defaults import *

class SettingsManager:
    """
    Gestore centralizzato delle configurazioni e dei temi dell'applicazione.

    Questa classe si occupa di:
    1. Mantenere lo stato delle impostazioni globali (zoom, tema, costanti).
    3. Gestire il sistema di temi dinamici, caricando file QSS e iniettando
       i colori della palette corretta (Light/Dark) prima di applicarli alla GUI.

    Attributes:
        K_VALUE (int): Parametro 'K' utilizzato negli algoritmi del modello (es. Top-K).
        WORKSPACE_DIRECTORY (str): Percorso della cartella di lavoro predefinita.
        ICON_SIZE (int): Dimensione in pixel delle icone dell'interfaccia.
        ZOOM_FACTOR (float): Livello di zoom attuale dell'interfaccia (1.0 = 100%).
        THEME_MODE (str): Modalità del tema attuale ("light" o "dark").
        CONSOLE_PALETTE (dict): Configurazione colori specifica per il widget console.
    """

    def __init__(self):
        """
        Inizializza il manager caricando i valori di default.

        I valori iniziali vengono letti dal file `defaults.py` (DEFAULTS_MAIN_VALUE)
        """
        self.K_VALUE = DEFAULTS_MAIN_VALUE["K_VALUE"]
        self.MIN_K_VALUE = DEFAULTS_MAIN_VALUE["MIN_K_VALUE"]
        self.MAX_K_VALUE = DEFAULTS_MAIN_VALUE["MAX_K_VALUE"]
        self.WORKSPACE_DIRECTORY = DEFAULTS_MAIN_VALUE["WORKSPACE_DIRECTORY"]
        self.ICON_SIZE = DEFAULTS_MAIN_VALUE["ICON_SIZE"]
        self.ZOOM_FACTOR = DEFAULTS_MAIN_VALUE["ZOOM_FACTOR"]
        self.MIN_ZOOM = DEFAULTS_MAIN_VALUE["MIN_ZOOM"]
        self.MAX_ZOOM = DEFAULTS_MAIN_VALUE["MAX_ZOOM"]
        self.TEXT_FONT = DEFAULTS_MAIN_VALUE["TEXT_FONT"]
        self.TEXT_SIZE = DEFAULTS_MAIN_VALUE["TEXT_SIZE"]
        self.THEME_MODE = DEFAULTS_MAIN_VALUE["THEME_MODE"]
        self.CONSOLE_PALETTE = DEFAULT_CONSOLE_PALETTE.copy()
        self.GRAPH_PALETTE = DEFAULT_GRAPH_PALETTE.copy()

    def get_stylesheet(self, filename: str) -> str:
        """
        Legge un file .qss e inietta dinamicamente i colori del tema corrente.

        Questo metodo agisce come un motore di template:
        1. Seleziona la palette (LIGHT o DARK) in base a `self.THEME_MODE`.
        2. Cerca il file nella cartella `styles/` risalendo di 3 livelli dalla root.
        3. Sostituisce i placeholder nel file .qss con i valori esadecimali reali.

        Args:
            filename (str): Il nome del file (es. "style.qss").

        Returns:
            str: Il contenuto CSS formattato e pronto per `setStyleSheet()`.
                 Restituisce stringa vuota in caso di errore.
        """
        # Recupera la palette giusta in base allo stato attuale
        if self.THEME_MODE == "light":
            self.PALETTE = LIGHT_PALETTE
        else:
            self.PALETTE = DARK_PALETTE

        # Logica di lettura file .qss
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Sale di un livello
        style_path = os.path.join(base_path, "styles", filename) 

        try:
            with open(style_path, "r") as f:
                return f.read().format(
                    primary_color=self.PALETTE["primary"],
                    secondary_color=self.PALETTE["secondary"],
                    terziary_color=self.PALETTE["terziary"],
                    app_color=self.PALETTE["app_color"],
                    text_main=self.PALETTE["text_main"],
                    border=self.PALETTE["border"],
                    bg_console=self.PALETTE["bg_console"],
                    border_console=self.PALETTE["border_console"],
                    bg_dark=self.PALETTE["bg_main"] 
                )
        except Exception as e:
            print(f"Errore style: {e}")
            return ""
    
    def get_stylesheets(self, *filenames: str) -> str:
        """
        Carica e unisce più file .qss in un'unica stringa CSS.

        Utile quando un widget necessita di stili provenienti da più file sorgente
        (es. uno stile base + uno stile specifico per componente).

        Args:
            *filenames (str): Argomenti variabili con i nomi dei file .qss.

        Returns:
            str: Una singola stringa contenente tutti i CSS concatenati.

        Example:
            >>> settings.get_stylesheets("base_style.qss", "sidebar.qss")
            "QWidget { background... } QListWidget { ... }"
        """
        combined_css = ""
        for name in filenames:
            css = self.get_stylesheet(name) 
            combined_css += css + "\n"
            
        return combined_css