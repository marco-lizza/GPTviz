import numpy as np

class ActionAttentionViewModel:
    def __init__(self):
        self.raw_attention_tensors = []
        self.tokens = []
        self.actions = []
        self.action_link_matrices=[]
        
        self.action_map = []
        self.projection_matrix = None
        self.action_lengths = None
        
        # Cache per le matrici calcolate (Lazy Loading)
        self._aggregated_cache = {}

    def load_data(self, attention_tensors, token_list, action_list,action_link_matrices=None):
        """
        Carica i dati grezzi e pre-calcola le matrici di proiezione.
        Da chiamare ogni volta che cambia il livello o il sample.
        """
        self._aggregated_cache = {}
        if not isinstance(attention_tensors, list):
            self.raw_attention_tensors = [np.array(attention_tensors)]
        else:
            self.raw_attention_tensors = [np.array(t) for t in attention_tensors]
            
        self.tokens = token_list
        self.actions = action_list

        self.action_link_matrices=action_link_matrices
        
        # Costruzione Action Map
        max_tokens = self.raw_attention_tensors[0].shape[0] if self.raw_attention_tensors else 0
        self.action_map = []
        current_idx = 0
        
        for action in action_list:
            n_parts = len(action.split('_')) 
            indices = [current_idx + i for i in range(n_parts) if current_idx + i < max_tokens]
            self.action_map.append(indices)
            current_idx += n_parts

        n_actions = len(self.actions)
        
        self.projection_matrix = np.zeros((n_actions, max_tokens), dtype=np.float32)
        self.action_lengths = np.zeros(n_actions, dtype=np.float32)
        
        for i, indices in enumerate(self.action_map):
            if indices:
                self.projection_matrix[i, indices] = 1.0
                self.action_lengths[i] = len(indices)
        
        # Evita divisione per zero
        self.action_lengths[self.action_lengths == 0] = 1.0 

    def get_aggregated_matrix(self, head_idx, normalize_by_row=True):
        """
        Restituisce la matrice di attenzione aggregata Azione x Azione.
        
        Args:
            head_idx (int): Indice della head.
            normalize_by_row (bool): 
                True -> Divide per src_len (Somma righe = 1, Probabilità).
                False -> Divide per src_len * tgt_len (Densità media).
        """
        if head_idx < 0 or head_idx >= len(self.raw_attention_tensors):
            return None
            
        cache_key = (head_idx, normalize_by_row)
        if cache_key in self._aggregated_cache:
            return self._aggregated_cache[cache_key]

        # --- CALCOLO VETTORIALIZZATO ---
        raw_matrix = self.raw_attention_tensors[head_idx] # (T, T)
        P = self.projection_matrix # (N, T)
        
        temp = P @ raw_matrix 
        
        sum_matrix = temp @ P.T # (N, N)
        
        # Normalizzazione
        if normalize_by_row:
            # Probabilità di transizione (Somma righe = 1)
            divisors = self.action_lengths[:, np.newaxis]
        else:
            # Densità media di connessione
            divisors = np.outer(self.action_lengths, self.action_lengths)
            
        result_matrix = sum_matrix / divisors
        
        # Salva in cache
        self._aggregated_cache[cache_key] = result_matrix
        return result_matrix

    def get_raw_matrix(self, head_idx):
        if 0 <= head_idx < len(self.raw_attention_tensors):
            return self.raw_attention_tensors[head_idx]
        return None

    def get_num_heads(self):
        return len(self.raw_attention_tensors)
    