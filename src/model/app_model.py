from PyQt6.QtCore import QObject, pyqtSignal

class AppModel(QObject):
    # Segnali per notificare i cambiamenti
    data_changed = pyqtSignal(list)      # Emesso quando la lista file cambia
    log_message = pyqtSignal(str)        # Emesso quando c'è un nuovo log
    processing_done = pyqtSignal(str)    # Emesso quando un calcolo finisce

    def __init__(self):
        super().__init__()
        self._items = []  # Il nostro "Database" interno

    def add_item(self, item_name):
        """Aggiunge un elemento alla logica e notifica gli ascoltatori."""
        if item_name not in self._items:
            self._items.append(item_name)
            self.log_message.emit(f"Modello: Aggiunto {item_name}")
            # Notifica che la lista è cambiata
            self.data_changed.emit(self._items) 
        else:
            self.log_message.emit(f"Errore: {item_name} esiste già.")

    def perform_operation(self, item_name):
        """Simula un'operazione complessa sui dati."""
        self.log_message.emit(f"Modello: Elaborazione di {item_name} in corso...")
        result = f"Risultato ({item_name}) [OK]"
        self.processing_done.emit(result)