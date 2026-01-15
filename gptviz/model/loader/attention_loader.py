import os
import pyarrow as pa
import torch
import shutil

from .metadata_scanner import MetadataScanner
from .arrow_tensor_accessor import ArrowTensorAccessor

class Attention_loader:
    """
    Gestore ad alto livello per il caricamento e la ricostruzione delle matrici di attenzione.
    
    Il suo compito principale è astrarre la complessità dello storage (file Arrow frammentati)
    e fornire al resto dell'applicazione matrici complete e ricostruite, pronte 
    per essere visualizzate.

    Attributes:
        base_path (str): Il percorso radice del workspace contenente i dati.
        scanner (MetadataScanner): Componente helper per l'indicizzazione dei file.
    """

    def __init__(self, base_path):
        """
        Inizializza il loader e lo scanner dei metadati.

        Args:
            base_path (str): Directory radice dove cercare i file `.arrow`.
        """
        self.base_path = base_path

        if not os.path.exists(self.base_path):
            try:
                os.makedirs(self.base_path)
            except OSError:
                raise OSError("Error during the creation of workspace directory")
        self.scanner = MetadataScanner(base_path)
        
        # Stato interno per la gestione del file aperto (Handle)
        self._current_filename = None
        self._accessor = None # Istanza di ArrowTensorAccessor
        self._source = None   # File handle (Memory Mapped File)

    def get_files_by_domain(self):
        """
        Recupera la struttura gerarchica dei file organizzati per dominio.
        
        Delegato allo scanner, utile per popolare menu o alberi di navigazione.

        Returns:
            Dict: Un dizionario {Dominio: [lista_file, ...]}.
        """
        return self.scanner.scan_domains()
    
    def load_file_in_workspace(self, file_path:str):
        """
        Riceve il path sorgente (dalla View) del file e lo copia nel workspace.
        """
        filename = os.path.basename(file_path)
        destination_path = os.path.join(self.base_path, filename)
        
        if os.path.exists(destination_path):
            raise FileExistsError()

        shutil.copy2(file_path, destination_path)



    def _ensure_file_open(self, filename: str):
        """
        Gestisce l'apertura intelligente (Lazy Loading) del file richiesto.
        
        Se il file richiesto è già aperto, non fa nulla. Se è diverso da quello
        attualmente in uso, chiude il precedente e apre il nuovo.

        Args:
            filename (str): Il nome del file da aprire (risolto poi dallo scanner).

        Raises:
            FileNotFoundError: Se il file non esiste nel percorso risolto.
        """
        if self._current_filename == filename and self._accessor is not None:
            return

        # Chiude il precedente se esiste per liberare risorse
        if self._source: 
            self._source.close()

        full_path = self.scanner._resolve_path(filename)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {full_path}")

        # Apertura e creazione dell'Accessor
        # Memory Map permette di caricare file più grandi della RAM disponibile
        self._source = pa.memory_map(full_path, 'r')
        reader = pa.ipc.open_file(self._source)
        table = reader.read_all()
        
        # Deleghiamo la complessità di navigazione all'Accessor
        self._accessor = ArrowTensorAccessor(table)
        self._current_filename = filename

    def get_metadata_only(self, filename: str):
        """
        Recupera i metadati (es. numero livelli, teste) senza caricare i tensori.

        Args:
            filename (str): Nome del file target.

        Returns:
            Dict: Metadati strutturali del file.
        """
        return self.scanner.get_metadata(filename)

    def get_reconstructed_matrix(self, filename: str, target_iter: int, level_idx: int, head_idx: int) -> torch.Tensor:
        """
        Ricostruisce la matrice di attenzione completa fino a una specifica iterazione.

        L'attenzione è spesso salvata in modo incrementale:
        1. Iterazione 0: Matrice completa del Prompt (NxN).
        2. Iterazione 1..K: Singoli vettori riga aggiunti per ogni token generato.

        Questo metodo assembla questi pezzi in un'unica matrice quadrata (o rettangolare)
        rappresentante lo stato dell'attenzione al passo `target_iter`.

        Algoritmo:
            1. Carica la matrice base (Prompt) dall'iterazione 0.
            2. Crea una matrice di zeri ("Canvas") di dimensione `(Prompt + Target)`.
            3. Copia la base nel quadrante in alto a sinistra.
            4. Itera da 1 a `target_iter`, recupera i vettori riga e li inserisce
               nelle posizioni corrispondenti.

        Args:
            filename (str): Il file dati da interrogare.
            target_iter (int): L'iterazione di generazione fino alla quale ricostruire.
            level_idx (int): Indice del layer.
            head_idx (int): Indice della testa.

        Returns:
            torch.Tensor: Matrice 2D (Float32) contenente l'attenzione ricostruita.

        Raises:
            IndexError: Se `target_iter` supera il numero di righe disponibili nel file.
        """
        self._ensure_file_open(filename)

        if target_iter >= self._accessor.num_rows:
            raise IndexError(f"Iteration {target_iter} out of range (Max: {self._accessor.num_rows - 1}).")

        base_tensor = self._accessor.get_tensor(0, level_idx, head_idx)

        prompt_len = base_tensor.shape[0]
        
        num_generated_tokens = target_iter 
        final_len = prompt_len + num_generated_tokens
        
        full_matrix = torch.zeros((final_len, final_len), dtype=torch.float32)
        full_matrix[:prompt_len, :prompt_len] = base_tensor
        
        
        for i in range(1, num_generated_tokens + 1):
            row_tensor = self._accessor.get_tensor(i, level_idx, head_idx)
        
            if row_tensor.dim() == 2:
                row_tensor = row_tensor.squeeze(0)
            
            current_len = row_tensor.shape[0]
            row_pos = prompt_len + i - 1
            
            safe_len = min(current_len, final_len)
            full_matrix[row_pos, :safe_len] = row_tensor[:safe_len]

        return full_matrix


    def get_level_matrices(self, filename: str, target_iter: int, level_idx: int) -> list[torch.Tensor]:
        """
        Recupera le matrici di attenzione ricostruite per tutte le teste (Heads) 
        di uno specifico livello (Layer).

        Il metodo consulta prima i metadati per determinare il numero di teste, 
        quindi itera invocando la ricostruzione per ciascuna di esse.

        Args:
            filename (str): Il file dati da interrogare.
            target_iter (int): L'iterazione di generazione target.
            level_idx (int): L'indice del layer desiderato.

        Returns:
            list[torch.Tensor]: Lista di matrici (una per ogni testa) di dimensione (NxN).
        """

        meta = self.get_metadata_only(filename)
        num_heads = meta.get('num_heads') 
        
        if num_heads is None:
            # Fallback o errore se il metadato non è presente
            raise ValueError(f"Key 'n_heads' not found in metadata of file {filename}")

        heads_list = []

        for head_idx in range(num_heads):
            # e _ensure_file_open controlla se il file è già aperto, 
            # questo loop è efficiente e non ricarica il file su disco ad ogni giro.
            matrix = self.get_reconstructed_matrix(filename, target_iter, level_idx, head_idx)
            heads_list.append(matrix)

        return heads_list

    def close(self):
        """
        Chiude il file memory-mapped e rilascia le risorse.  
        """
        if self._source:
            self._source.close()
            self._source = None
            self._accessor = None
            self._current_filename = None
