from src.model.app_model import AppModel
from src.view.components.workspace_widget import WorkspaceView

class Workspace_controller:
    """
    Gestisce la logica dell'area di lavoro principale (Workspace).

    Questo controller è il cuore della visualizzazione dati. Si occupa di coordinare
    il rendering delle matrici di attenzione e la gestione dello stato visivo
    dell'area centrale dell'applicazione.
    
    A differenza di altri controller che gestiscono input utente, questo componente
    reagisce principalmente ai cambiamenti di stato del Modello per aggiornare la grafica.

    Attributes:
        model (AppModel): Riferimento al modello dati principale.
        workspace_view (WorkspaceView): Riferimento al widget che disegna le matrici/grafici.
    """

    def __init__(self, model: AppModel, workspace_view: WorkspaceView):
        """
        Inizializza il controller del Workspace.

        Args:
            model (AppModel): L'istanza del modello dati.
            workspace_view (WorkspaceView): L'istanza della vista di lavoro.
        """
        self.model = model
        self.workspace_view = workspace_view

        self.set_up_binding()

    def set_up_binding(self):
        """
        Configura le connessioni dirette (Model -> View) per la visualizzazione.

        Connections:
            1. `model.head_matrix_loaded` -> `view.visualize_attentions_matrix`:
               Quando il modello ha pronto un tensore/matrice, la vista lo riceve
               immediatamente per il rendering grafico.
            
            2. `model.clear_workspace` -> `view.reset_view`:
               Quando il modello richiede pulizia (es. cambio file), la vista
               rimuove tutti i grafici correnti.
        """
        self.model.head_matrix_loaded.connect(self.workspace_view.visualize_attentions_matrix)
        self.model.clear_workspace.connect(self.workspace_view.reset_view)