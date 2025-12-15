import torch

class Attention_data:
    """
    Classe contenitore per i dati di attention.
    Mantiene la struttura gerarchica e fornisce metodi di accesso.
    """
    def __init__(self, raw_data, metadata=None):
        self._data = raw_data  # Struttura: [iteration][level][head] -> matrix
        self.metadata = metadata or {}

    def get_data(self):
        return self._data
    
    def get_metadata(self):
        return [self.metadata.get("num_iterations", 0),self.metadata.get("num_levels", 0),self.metadata.get("num_heads", 0)]
            

    def get_matrix(self, iteration_idx, level_idx, head_idx, as_tensor=True):
        """
        Recupera la matrice di attention specifica per iterazione, livello e head.
        """
        try:
            matrix_data = self._data[iteration_idx][level_idx][head_idx]
            
            if as_tensor:
                return torch.tensor(matrix_data)
            return matrix_data
            
        except IndexError:
            raise IndexError(f"Indici fuori range: Iter={iteration_idx}, Level={level_idx}, Head={head_idx}")

    def get_level_tensor(self, iteration_idx, level_idx):
        try:
            level_data = self._data[iteration_idx][level_idx]
            return torch.tensor(level_data)
        except IndexError:
            raise IndexError(f"Indici fuori range: Iter={iteration_idx}, Level={level_idx}")

    def info(self):
        """Fornisce informazioni sulla struttura caricata."""
        num_iters = len(self._data)
        num_levels = len(self._data[0]) if num_iters > 0 else 0
        num_heads = len(self._data[0][0]) if num_levels > 0 else 0
        
        result=f"Iterazioni totali: {num_iters} - Livelli per iterazione: {num_levels} - Heads per livello: {num_heads}"
        return result