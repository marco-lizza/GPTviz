from src.model.app_model import AppModel
from src.view.components.toolbar_widget import Toolbar

class Tooolbar_controller:
    """
    Gestisce le interazioni dell'utente con la toolbar.

    Questo controller funge da ponte tra i comandi impartiti dall'utente tramite i menu
    (es. File ecc..) e la logica di business dell'applicazione.
    Intercetta i segnali della vista e invoca i metodi corrispondenti nel modello.

    Attributes:
        model (AppModel): Riferimento al modello dati principale.
        toolbar_view (Toolbar): Riferimento al widget della toolbar.
    """

    def __init__(self, model: AppModel, toolbar_view: Toolbar):
        """
        Inizializza il controller del menu superiore.

        Args:
            model (AppModel): L'istanza del modello dati dell'applicazione.
            toolbar_view (Toolbar): L'istanza della vista toolbar.
        """
        self.model = model
        self.toolbar_view = toolbar_view

        self.set_up_binding()

    def set_up_binding(self):
        """
        Configura i listener per le azioni del menu (View -> Controller).

        Collega i segnali emessi dai pulsanti/voci del menu ai metodi di gestione
        interni di questo controller o a metodi del model.
        
        Mappings:
            * `view.load_file_names` -> `handle_load_file_names()`
            * `view.clear_console` -> `clear_console()`
            * `view.import_requested` -> `self.model.import_file_requested()`
        """
        self.toolbar_view.load_file_names.connect(self.handle_load_file_names)
        self.toolbar_view.clear_console.connect(self.clear_console)
        self.toolbar_view.import_requested.connect(self.model.import_file_requested)

    def handle_load_file_names(self):
        """
        Gestisce la richiesta di caricamento dei file dal workspace.

        Invocato quando l'utente seleziona l'azione di aggiornamento dello workspace. Ordina al modello di scansionare o caricare
        la lista dei file disponibili.
        """
        self.model.load_file_names()

    def clear_console(self):
        """
        Gestisce il comando di pulizia della console.

        Invocato quando l'utente clicca su "Clean console". Invia il comando al modello,
        che a sua volta emetterà il segnale `erase_console` per notificare tutti 
        i componenti interessati (come il ConsoleController).
        """
        self.model.clear_console()