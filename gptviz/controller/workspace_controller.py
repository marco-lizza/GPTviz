from ..model.app_model import AppModel
from ..view.workspace_widget.workspace_widget import WorkspaceView

import numpy as np

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
            1. `model.level_matrices_loaded` -> `view.visualize_attentions`:
               Quando il modello ha pronta una lista di tensori/matrici, la vista la riceve
               immediatamente per il rendering grafico.
            
            2. `model.clear_workspace` -> `view.reset_view`:
               Quando il modello richiede pulizia (es. cambio file), la vista
               rimuove tutti i grafici correnti.
        """
        self.model.level_matrices_loaded.connect(self.manage)
        self.model.clear_workspace.connect(self.workspace_view.reset_view)
    def manage(self, matrices_list, token_list, action_list):
        action_link_matrices = []
        
        # Determino la dimensione della matrice quadrata in base al numero di azioni
        num_actions = len(action_list) 

        for i in range(len(matrices_list)):
                    full_random_matrix = np.random.randint(2, size=(num_actions, num_actions))
                    random_link_matrix = np.tril(full_random_matrix, k=-1)
                    
                    action_link_matrices.append(random_link_matrix)

        # Passo la nuova lista 'action_link_matrices' alla funzione di visualizzazione
        self.workspace_view.visualize_attentions(
            matrices_list, 
            token_list, 
            action_list, 
            action_link_matrices
        )