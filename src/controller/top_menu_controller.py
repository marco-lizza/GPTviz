from src.model.app_model import AppModel
from src.view.components.menu_widget import TopMenuBar

class Top_menu_controller:
    """
    Gestisce le interazioni dell'utente con la barra dei menu superiore (Top Menu Bar).

    Questo controller funge da ponte tra i comandi impartiti dall'utente tramite i menu
    (es. File ecc..) e la logica di business dell'applicazione.
    Intercetta i segnali della vista e invoca i metodi corrispondenti nel modello.

    Attributes:
        model (AppModel): Riferimento al modello dati principale.
        top_menu_view (TopMenuBar): Riferimento al widget della barra dei menu.
    """

    def __init__(self, model: AppModel, top_menu_view: TopMenuBar):
        """
        Inizializza il controller del menu superiore.

        Args:
            model (AppModel): L'istanza del modello dati dell'applicazione.
            top_menu_view (TopMenuBar): L'istanza della vista della barra dei menu.
        """
        self.model = model
        self.top_menu_view = top_menu_view

        self.set_up_binding()

    def set_up_binding(self):
        """
        Configura i listener per le azioni del menu (View -> Controller).

        Collega i segnali emessi dai pulsanti/voci del menu ai metodi di gestione
        interni di questo controller.
        
        Mappings:
            * `view.open_options` -> `open_options()`
            * `view.load_file_names` -> `handle_load_file_names()`
            * `view.clear_console` -> `clear_console()`
        """
        self.top_menu_view.open_options.connect(self.open_options)
        self.top_menu_view.load_file_names.connect(self.handle_load_file_names)
        self.top_menu_view.clear_console.connect(self.clear_console)

    def handle_load_file_names(self):
        """
        Gestisce la richiesta di caricamento dei file dal workspace.

        Invocato quando l'utente seleziona l'azione di aggiornamento dello workspace. Ordina al modello di scansionare o caricare
        la lista dei file disponibili.
        """
        self.model.load_file_names()
        
    def open_options(self):
        """
        Gestisce la richiesta di apertura del pannello opzioni.

        Invocato dal menu opzioni. Sollecita il modello a innescare il processo
        di apertura del dialog di configurazione (che verrà poi gestito dal Main Controller).
        """
        self.model.open_option()

    def clear_console(self):
        """
        Gestisce il comando di pulizia della console.

        Invocato quando l'utente clicca su "Clear Console". Invia il comando al modello,
        che a sua volta emetterà il segnale `erase_console` per notificare tutti 
        i componenti interessati (come il ConsoleController).
        """
        self.model.clear_console()