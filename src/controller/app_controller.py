class AppController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # --- CONNESSIONI (BINDING) ---

        # Connessioni dall view al controller
        self.view.import_requested.connect(self.handle_import)
        self.view.process_requested.connect(self.handle_process)

        # Connessioni indirette dal modello alla view

        # Quando il modello cambia la lista -> aggiorna sidebar
        self.model.data_changed.connect(self.view.update_sidebar)
        # Quando il modello ha un log -> scrivi in console
        self.model.log_message.connect(self.view.update_console)
        # Quando il modello finisce un calcolo -> aggiorna workspace
        self.model.processing_done.connect(self.view.update_workspace)

    def handle_import(self):
        """ESEMPIO : Logica di controllo per l'importazione."""
        import random
        fake_files = ["Dato1.csv", "Dato2.csv", "Dato3.csv"]
        new_item = random.choice(fake_files)
        
        # Chiede al modello di aggiungere i dati
        self.model.add_item(new_item)

    def handle_process(self, item_name):
        """ESEMPIO : Logica di controllo per l'elaborazione."""
        self.model.perform_operation(item_name)