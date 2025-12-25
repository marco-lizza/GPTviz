"""
Modulo di configurazione globale dell'applicazione.

Questo modulo espone l'istanza Singleton `settings`.
Utilizzando questo oggetto condiviso, si garantisce che qualsiasi modifica alle 
preferenze (es. cambio tema) sia immediatamente visibile a tutti i componenti 
dell'applicazione senza dover passare l'oggetto manualmente.
"""

from .manager import SettingsManager

# Istanziazione del Singleton
settings = SettingsManager()
"""
Istanza globale condivisa di :class:`SettingsManager`.

Questa variabile deve essere importata ovunque sia necessario accedere o modificare
le configurazioni. Non istanziare nuovamente `SettingsManager` manualmente 
nel codice client per evitare disallineamenti di stato.

Usage:
    >>> from src.config import settings
    >>> current_theme = settings.THEME_MODE
    >>> ...
"""