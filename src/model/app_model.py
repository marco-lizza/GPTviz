from PyQt6.QtCore import QObject, pyqtSignal
from .loader.attention_loader import Attention_loader
import torch
import ast

from src.config import settings

class AppModel(QObject):
    """
    Modello principale dell'applicazione (Main Model).

    Questa classe centralizza la gestione dello stato e della logica di business.

    Attributes:
        base_path (str): Directory di lavoro letta dai settings globali.
        loader (Attention_loader): Istanza del gestore I/O per i file Arrow.
        actual_file (str): Nome del file attualmente selezionato/caricato.
    """

    base_path = settings.WORKSPACE_DIRECTORY

    # Definizione Segnali
    file_name_loaded = pyqtSignal(dict)   
    log_message = pyqtSignal(str) 
    erase_console = pyqtSignal()
    attentions_loaded = pyqtSignal(dict)
    head_matrix_loaded = pyqtSignal(torch.Tensor,list)
    level_matrices_loaded = pyqtSignal(list, list)
    clear_workspace = pyqtSignal()

    def __init__(self):
        """Inizializza il modello e il loader interno."""
        super().__init__()
        self.loader = Attention_loader(self.base_path) 
        self.actual_file = ""

    def load_file_names(self):
        """
        Scansiona la directory di lavoro e notifica la lista dei file disponibili.

        Esegue le seguenti operazioni:
        1. Interroga il loader per ottenere i file raggruppati per dominio.
        2. Emette un log di successo.
        3. Emette `file_name_loaded` per aggiornare la sidebar.
        4. Pulisce il workspace grafico (`clear_workspace`).

        In caso di errore, emette un segnale `log_message` formattato come errore.
        """
        try:
            files = self.loader.get_files_by_domain()
            self.log_message.emit(f"<succ>.arrow file into <i>workspace</i> directory <b>loaded<b></succ>")
            self.file_name_loaded.emit(files)
            self.clear_workspace.emit()
        except Exception as e:
            self.log_message.emit(f"<erro>{e}</erro>")

    def load_metadata_of_file(self, file_name: str):
        """
        Carica i metadati del file specificato e prepara l'ambiente.

        Non carica ancora l'intera matrice dei dati, ma legge solo l'intestazione
        (numero di teste, livelli, iterazioni) necessaria per costruire l'interfaccia
        di navigazione (Attention Navigator).

        Args:
            file_name (str): Il nome del file .arrow da caricare.
        """
        self.actual_file = file_name
        
        try:
            self.log_message.emit(f"<gene>File loading: <i>{self.base_path}/{self.actual_file}</i></gene>")
            
            # Recupero solo metadati leggeri
            self.actual_attentions_metadata = self.loader.get_metadata_only(self.actual_file)
            
            # Notifica la UI
            self.attentions_loaded.emit(self.actual_attentions_metadata)
            self.log_message.emit("<succ>Loading done</succ>")

            # Reset della vista grafica
            self.clear_workspace.emit()
        except Exception as e:
           self.log_message.emit(f"<erro>{e}</erro>")

    def get_head(self, iter_idx: int, lev_idx: int, head_idx: int):
        """
        Richiede la ricostruzione e l'invio della matrice di attenzione specifica.

        Delega al loader la complessità di estrazione e assemblaggio del tensore
        per la specifica tripla (Iterazione, Livello, Testa).
        Il risultato viene emesso tramite il segnale `head_matrix_loaded`.

        Args:
            iter_idx (int): Indice dell'iterazione temporale.
            lev_idx (int): Indice del layer del modello.
            head_idx (int): Indice della testa di attenzione.
        """
        try:
            matrix = self.loader.get_reconstructed_matrix(
                self.actual_file, iter_idx, lev_idx, head_idx
            )

            raw_action_list=self.actual_attentions_metadata["action_list"]

            if isinstance(raw_action_list, str):
                action_list = ast.literal_eval(raw_action_list)
            else:
                action_list = raw_action_list
            token_list=[]

            for action in action_list:
                for section in action.split("_"):
                    token_list.append(section)
                    
            self.log_message.emit(f"<info>Iteration: {iter_idx} - Level: {lev_idx} - Head: {head_idx} selected</info>")
            self.head_matrix_loaded.emit(matrix,token_list)
        except IndexError as e:
            self.log_message.emit(f"<erro>{e}</erro>")

    def get_level(self, iter_idx: int, lev_idx: int):
        """
        Richiede la ricostruzione e l'invio di TUTTE le matrici di attenzione
        per un determinato livello (Layer).

        Recupera la lista delle matrici (una per ogni testa) tramite il loader
        e prepara la lista dei token corrispondenti.
        Il risultato viene emesso tramite il segnale `level_matrices_loaded`.

        Args:
            iter_idx (int): Indice dell'iterazione temporale.
            lev_idx (int): Indice del layer del modello.
        """
        try:
            matrices_list = self.loader.get_level_matrices(
                self.actual_file, iter_idx, lev_idx
            )

            raw_action_list = self.actual_attentions_metadata["action_list"]

            if isinstance(raw_action_list, str):
                action_list = ast.literal_eval(raw_action_list)
            else:
                action_list = raw_action_list
            
            token_list = []
            for action in action_list:
                for section in action.split("_"):
                    token_list.append(section)

            self.log_message.emit(f"<info>Iteration: {iter_idx} - Level: {lev_idx} selected</info>")
            
            # Emette la lista di matrici e la lista di token.
            self.level_matrices_loaded.emit(matrices_list, token_list)

        except (IndexError, ValueError) as e:
            self.log_message.emit(f"<erro>{e}</erro>")

    def clear_console(self):
        """Emette il segnale per pulire il testo della console di sistema."""
        self.erase_console.emit()