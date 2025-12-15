import json
import os

from .attention import Attention_data

class Attention_loader:
    """
    Classe responsabile del caricamento del file JSON.
    """
    def __init__(self, base_path="workspace/"):
        self.base_path = base_path

    def load(self, filename):
        # Se il filename non è un percorso assoluto, lo uniamo al base_path
        if not os.path.isabs(filename):
            full_path = os.path.join(self.base_path, filename)
        else:
            full_path = filename
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Il file {full_path} non esiste.")

        try:
            with open(full_path, 'r') as f:
                content = json.load(f)
            
            if "data" not in content:
                raise ValueError("Il file JSON non contiene la chiave 'data'.")
                
            return Attention_data(content["data"], content.get("metadata"))
            
        except json.JSONDecodeError:
            raise ValueError(f"Il file {full_path} non è un JSON valido.")
        except Exception as e:
            raise RuntimeError(f"Errore imprevisto durante il caricamento: {e}")
        
    def list_files(self):
        if not os.path.exists(self.base_path):
            return []

        return [f for f in os.listdir(self.base_path) if f.endswith('.json')]
        