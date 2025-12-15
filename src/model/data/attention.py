import torch

class Attention_data:
    """
    Classe contenitore per i dati di attention.
    Mantiene la struttura gerarchica e fornisce metodi di accesso.
    """
    def __init__(self, raw_data, metadata=None):
        self._data = raw_data
        self.metadata = metadata or {}

    def get_data(self):
        return self._data
    
    def get_metadata(self):
        return [self.metadata.get("num_iterations", 0),self.metadata.get("num_levels", 0),self.metadata.get("num_heads", 0)]
            

    def get_matrix(self, iteration_idx, level_idx, head_idx, as_tensor=True):
        """
        Recupera la matrice di attention.
        
        - Se iteration_idx == 0: Restituisce la matrice del prompt.
        - Se iteration_idx > 0: RICOSTRUISCE la matrice accumulando la storia 
          dall'iterazione 0 fino a quella richiesta.
        
        """
        try:
            base_data = self._data[0][level_idx][head_idx]
            base_tensor = torch.tensor(base_data)
        except IndexError:
            raise IndexError(f"Dati non trovati per Level={level_idx}, Head={head_idx} all'iterazione 0.")

        if iteration_idx == 0:
            return base_tensor if as_tensor else base_tensor.tolist()

        # SE RICHIESTA ITERAZIONE > 0: Inizia la ricostruzione
        rows = []

        for i in range(base_tensor.shape[0]):
            rows.append(base_tensor[i])

        for i in range(1, iteration_idx + 1):
            try:
                step_data = self._data[i][level_idx][head_idx]
                step_tensor = torch.tensor(step_data)
                
                if step_tensor.dim() > 1:
                    step_tensor = step_tensor.squeeze()
                
                rows.append(step_tensor)
            except IndexError:
                 break

        if not rows:
            return torch.empty(0)

        max_seq_len = len(rows[-1])
        total_rows = len(rows)

        full_matrix = torch.zeros((total_rows, max_seq_len))

        for i, row in enumerate(rows):
            current_len = len(row)
            full_matrix[i, :current_len] = row

        if as_tensor:
            return full_matrix
        else:
            return full_matrix.tolist()

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