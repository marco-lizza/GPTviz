from ..model.app_model import AppModel
from ..view.sidebar_widget import SidebarView

class Sidebar_controller:
    """
    Gestisce la logica della barra laterale (Sidebar), focalizzandosi sulla navigazione dei file.

    Questo controller coordina l'interazione tra la lista dei file presenti nel modello
    e la loro rappresentazione visuale nella GUI. Si occupa di reagire alla selezione
    dell'utente per avviare il caricamento dei dati specifici del file scelto.

    Attributes:
        model (AppModel): Riferimento al modello dati principale.
        sidebar_view (SidebarView): Riferimento al widget della vista che contiene la lista dei file.
    """

    def __init__(self, model:AppModel, sidebar_view:SidebarView):
        """
        Inizializza il controller della sidebar.

        Args:
            model (AppModel): L'istanza del modello dati condiviso.
            sidebar_view (SidebarView): L'istanza della vista laterale.
        """
        self.model = model
        self.sidebar_view = sidebar_view

        self.set_up_binding()

    def set_up_binding(self):
        """
        Configura le connessioni (segnali/slot) per la gestione dei file.

        Stabilisce due flussi distinti:
        1. **Interazione Utente (View -> Controller -> Model):**
           Quando un file viene cliccato nella lista (`file_clicked`), il controller
           intercetta l'evento tramite `handle_file_clicked` per istruire il modello.
        
        2. **Aggiornamento Dati (Model -> View):**
           Quando il modello ha caricato la lista dei nomi dei file (`file_name_loaded`),
           aggiorna direttamente il widget della lista (`update_sidebar`), 
           bypassando logiche intermedie del controller.
        """
        # Evento utente: Click su un file nella lista
        self.sidebar_view.file_list.file_clicked.connect(self.handle_file_clicked)
        
        # Evento sistema: Dati caricati, aggiorna la lista visiva
        self.model.file_name_loaded.connect(self.sidebar_view.file_list.update_sidebar)

    def handle_file_clicked(self, item_name: str):
        """
        Gestisce l'evento di selezione di un file dalla lista.

        Viene invocato quando l'utente clicca su un elemento della sidebar.
        Questo metodo ordina al modello di caricare i metadati associati al file selezionato,
        preparando il terreno per le visualizzazioni successive (es. Attention Navigator).

        Args:
            item_name (str): Il nome univoco del file cliccato.
        """
        self.model.load_metadata_of_file(item_name)