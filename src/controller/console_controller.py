from src.model.app_model import AppModel
from src.view.main_window_components.console_widget import ConsoleView

class Console_controller:
    """
    Gestisce il flusso di output dei messaggi di sistema verso la console dell'interfaccia.

    Questo controller ascolta i segnali di logging emessi dal modello e si assicura
    che vengano visualizzati correttamente nella finestra di console (View).

    Attributes:
        model (AppModel): Riferimento al modello dati principale che emette i messaggi di log.
        console_view (ConsoleView): Riferimento al widget della vista che mostra il testo (es. un TextEdit).
    """

    def __init__(self, model:AppModel, console_view:ConsoleView):
        """
        Inizializza il controller della console.

        Args:
            model (AppModel): L'istanza del modello dati condiviso.
            console_view (ConsoleView): L'istanza della vista dedicata alla console.
        """
        self.model = model
        self.console_view = console_view

        self.set_up_binding()

    def set_up_binding(self):
        """
        Configura i listener per i segnali di logging e manutenzione console.

        Stabilisce le seguenti connessioni:
        1. `log_message` -> `update_console`: Intercetta i messaggi per aggiungerli alla vista.
        2. `erase_console` -> `view.clear_console`: Collega direttamente il segnale di pulizia
           al metodo di pulizia della vista, bypassando logiche intermedie.
        """
        self.model.log_message.connect(self.update_console)
        self.model.erase_console.connect(self.console_view.clear_console)

    def update_console(self, message: str):
        """
        Riceve un messaggio dal modello e lo accoda (append) nella vista console.

        Args:
            message (str): La stringa di testo da visualizzare. Può contenere
                informazioni di debug, errori o stati di avanzamento.
        """
        self.console_view.append_log(message)