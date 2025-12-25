import pyarrow as pa
import torch
import numpy as np

class ArrowTensorAccessor:
    """
    Gestisce l'accesso a basso livello e ad alte prestazioni a una Table Arrow.

    Struttura Dati Attesa:
        La tabella Arrow deve avere una colonna 'data' con una struttura nidificata:
        List (Iterazioni) -> List (Livelli) -> List (Teste) -> List/FixedSizeList (Matrice).

    Attributes:
        table (pa.Table): La tabella PyArrow sorgente caricata in memoria (RAM o Memory Map).
        data_column (pa.ChunkedArray): Riferimento diretto alla colonna 'data' per 
            evitare l'overhead di lookup dizionario ad ogni accesso.
        num_rows (int): Numero totale di righe (iterazioni) disponibili.
    """

    def __init__(self, table: pa.Table):
        """
        Inizializza l'accessore e pre-carica i riferimenti alle colonne.

        Args:
            table (pa.Table): La tabella PyArrow contenente i dati delle attention heads.
        """
        self.table = table
        # Cache della colonna dati per evitare lookup ripetuti (ottimizzazione accesso)
        self.data_column = self.table['data']
        self.num_rows = self.table.num_rows

    def get_tensor(self, iter_idx: int, level_idx: int, head_idx: int) -> torch.Tensor:
        """
        Estrae un tensore PyTorch (Float32) da una specifica coordinata gerarchica.

        Il metodo esegue la navigazione della struttura nidificata di Arrow, converte
        i dati binari in NumPy e infine li trasforma in un Tensore PyTorch 2D.

        Processo di conversione:
        1. **Navigazione**: Discesa nella gerarchia Arrow (Iter -> Level -> Head).
        2. **Estrazione**: Recupero dei valori grezzi.
        3. **Copy**: I dati vengono copiati (`.copy()`) per svincolarli dalla memoria 
           read-only di Arrow e renderli scrivibili/gestibili da PyTorch.
        4. **Reshape**: I dati piatti vengono rimodellati nella matrice [Rows, Cols].

        Args:
            iter_idx (int): Indice dell'iterazione (row index nella Table).
            level_idx (int): Indice del livello (layer) del modello.
            head_idx (int): Indice della testa di attenzione (attention head).

        Returns:
            torch.Tensor: Un tensore 2D di tipo `torch.float32`. 
            Le dimensioni dipendono dalla matrice salvata (es. [SeqLen, SeqLen]).

        Raises:
            IndexError: Se uno degli indici forniti esce dai limiti della struttura dati.
            RuntimeError: Se si verifica un errore imprevisto durante la conversione 
                          (es. formato dati Arrow corrotto o non conforme).
        """
        try:
            iter_scalar = self.data_column[iter_idx]

            # Accesso alla lista dei livelli (ListArray)
            levels_array = iter_scalar.values 

            # Accesso al livello specifico
            head_scalar = levels_array[level_idx]
            
            # Accesso alla lista delle teste
            heads_array = head_scalar.values
            
            # Accesso alla matrice specifica (Head)
            matrix_scalar = heads_array[head_idx]
            
            # Estrazione e Flattening
            rows_array = matrix_scalar.values
            flat_arrow_data = rows_array.flatten()
            
            # Conversione NumPy
            # PyTorch  richiede memoria scrivibile mentre Arrow
            # potrebbe fornire view read-only 
            numpy_flat = flat_arrow_data.to_numpy(zero_copy_only=False).copy()
            
            # Creazione del Tensore
            tensor_flat = torch.from_numpy(numpy_flat).float()
            
            # Reshape dinamico basato sulla lunghezza dei dati
            n_rows = len(rows_array)
            # Calcola n_cols solo se ci sono righe, altrimenti 0 per evitare division by zero
            n_cols = len(rows_array[0]) if n_rows > 0 else 0
            
            return tensor_flat.view(n_rows, n_cols)
            
        except IndexError:
            # Rilancia l'errore con contesto aggiuntivo per il debugging
            raise IndexError(f"Indici non validi: Iter={iter_idx}, Lev={level_idx}, Head={head_idx}")
        except Exception as e:
            raise RuntimeError(f"Errore accesso Arrow: {e}")