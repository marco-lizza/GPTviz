import os
import pyarrow as pa
from collections import defaultdict

class MetadataScanner:
    """
    Componente specializzato nella scansione rapida del filesystem e dei metadati Arrow.

    Questa classe è progettata per essere estremamente leggera:
    invece di caricare l'intero contenuto dei file `.arrow` ,
    apre solo il footer/header del file per estrarre le informazioni essenziali.

    Attributes:
        base_path (str): Il percorso della directory contenente i file da scansionare.
    """
    
    def __init__(self, base_path: str):
        """
        Inizializza lo scanner su un percorso specifico.

        Args:
            base_path (str): Path assoluto o relativo alla cartella dati.
        """
        self.base_path = base_path

    def _resolve_path(self, filename: str) -> str:
        """
        Risolve il percorso completo del file.

        Gestisce sia percorsi assoluti che relativi rispetto a `self.base_path`.

        Args:
            filename (str): Nome del file o percorso.

        Returns:
            str: Il percorso assoluto normalizzato.
        """
        return filename if os.path.isabs(filename) else os.path.join(self.base_path, filename)

    def _decode_dict(self, binary_dict: dict) -> dict:
        """
        Decodifica i metadati binari di PyArrow in tipi Python nativi.

        Args:
            binary_dict (dict): Il dizionario grezzo estratto da `reader.schema.metadata`.

        Returns:
            dict: Dizionario pulito con chiavi stringa e valori tipizzati.
        """
        if not binary_dict: return {}
        decoded = {}
        for k, v in binary_dict.items():
            k_str = k.decode('utf-8')
            v_str = v.decode('utf-8')
            # Inferenza tipo semplice: se è tutto cifre, è un int
            decoded[k_str] = int(v_str) if v_str.isdigit() else v_str
        return decoded
    
    def get_metadata(self, filename: str) -> dict:
        """
        Estrae i metadati completi di un singolo file senza caricarne il body.

        Args:
            filename (str): Il nome del file `.arrow` da ispezionare.

        Returns:
            dict: Un dizionario contenente metadati come 'num_heads', 'num_levels', 
                  'domain', ecc. Ritorna un dict vuoto in caso di errore.

        Raises:
            FileNotFoundError: Se il file non esiste (sollevato prima del try/except).
        """
        full_path = self._resolve_path(filename)
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File non trovato: {full_path}")

        try:
            with pa.OSFile(full_path, 'rb') as source:
                # ipc.open_file legge solo lo schema (Footer/Header) - Istantaneo
                reader = pa.ipc.open_file(source)
                return self._decode_dict(reader.schema.metadata)
        except Exception as e:
            print(f"Errore lettura metadati per {filename}: {e}")
            return {}

    def scan_domains(self) -> dict:
        """
        Scansiona la directory base e raggruppa i file per 'domain'.

        Itera su tutti i file `.arrow` nella cartella `base_path`, legge i loro
        metadati e costruisce una mappa che associa ogni dominio alla lista
        di file che vi appartengono.

        Returns:
            dict: Un dizionario nella forma `{ 'blocksworld': ['file1.arrow', ...], 'news': [...] }`.
                  Ritorna un dizionario vuoto se la directory base non esiste.
        """
        if not os.path.exists(self.base_path): return {}
        
        domain_map = defaultdict(list)
        files = [f for f in os.listdir(self.base_path) if f.endswith('.arrow')]
        
        for filename in files:
            full_path = self._resolve_path(filename)
            try:
                with pa.OSFile(full_path, 'rb') as source:
                    # Legge solo lo schema (Footer/Header)
                    reader = pa.ipc.open_file(source)
                    meta = self._decode_dict(reader.schema.metadata)
                    
                    # Raggruppamento per chiave 'domain'
                    if 'domain' in meta:
                        domain_map[meta['domain']].append(filename)
            except Exception as e:
                # Logga l'errore ma continua la scansione per gli altri file
                print(f"Skipping {filename}: {e}")
                
        return dict(domain_map)