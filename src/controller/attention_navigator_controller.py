from src.model.app_model import AppModel
from src.view.main_window_components.attentions_navigator_widget import Attention_navigator_widget

class Attention_navigator_controller:
    """
    Gestisce la logica del navigatore degli 'Attention Levels' 

    Questo controller agisce da intermediario tra il modello dati (che contiene 
    i tensori e le matrici di attenzione) e la vista che permette di navigare 
    tra le varie iterazioni e livelli.

    Attributes:
        model (AppModel): Riferimento al modello dati principale dell'applicazione.
        attention_navigator_view (Attention_navigator_widget): La vista specifica che mostra
            l'albero di navigazione dei livelli.
    """

    def __init__(self, model:AppModel, attention_navigator_view:Attention_navigator_widget):
        """
        Inizializza il controller del navigatore e configura i listener.

        Args:
            model (AppModel): L'istanza del modello dati condiviso.
            attention_navigator_view (Attention_navigator_widget): L'istanza del widget/vista UI del navigatore.
        """
        self.model = model
        self.attention_navigator_view = attention_navigator_view

        self.set_up_binding()

    def set_up_binding(self):
        """
        Configura le connessioni bidirezionali (segnali/slot) tra Modello e Vista.

        Stabilisce due flussi di comunicazione:
        1. Modello -> Vista: Quando i dati vengono caricati (`attentions_loaded`), 
           aggiorna la UI.
        2. Vista -> Modello: Quando l'utente clicca un livello (`level_clicked`), 
           richiede al modello di recuperare i dati specifici.
        """
        # Quando il modello ha finito di caricare i dati, aggiorna la vista
        self.model.attentions_loaded.connect(self.update_attention_navigator)
        
        # Quando l'utente clicca sulla vista, notifica il controller di procedere con il reperimento delle informazioni
        self.attention_navigator_view.level_clicked.connect(self.level_clicked)

        # Resetta la vista del navigator quando viene aggiornato il workspace o viene fatto un import
        self.model.clear_navigator.connect(self.attention_navigator_view.reset_view)

    def update_attention_navigator(self, attention_metadata: dict):
        """
        Aggiorna la struttura visuale del navigatore in base ai metadati ricevuti.

        Viene chiamata automaticamente quando il segnale `attentions_loaded` viene
        emesso dal modello.

        Args:
            attention_metadata (dict): Un dizionario contenente la struttura topologica 
                dell'attenzione caricata. Deve contenere le chiavi:
                * 'num_iterations': (int) Numero totale di iterazioni.
                * 'num_levels': (int) Numero di livelli (layers) del modello.
        """
        self.attention_navigator_view.update_sidebar(
            attention_metadata.get("num_iterations"),
            attention_metadata.get("num_levels")
        )

    def level_clicked(self, iter_idx: int, lev_idx: int):
        """
        Gestisce l'evento di selezione di una specifico livello di attenzione.

        Questo metodo viene invocato dalla vista quando l'utente clicca su un 
        elemento specifico della navigazione. Inoltra la richiesta al modello 
        per recuperare o visualizzare i dati di quel livello.

        Args:
            iter_idx (int): Indice dell'iterazione selezionata.
            lev_idx (int): Indice del livello (layer) selezionato.
        """
        self.model.get_level(iter_idx, lev_idx)