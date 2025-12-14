class Toolbar_controller:
    def __init__(self, model, toolbar_view):
        self.model = model
        self.toolbar_view = toolbar_view

        self.set_up_binding()

    def set_up_binding(self):
        self.toolbar_view.import_requested.connect(self.handle_import)

    def handle_import(self):
        """ESEMPIO : Logica di controllo per l'importazione."""
        import random
        fake_files = ["Dato1.csv", "Dato2.csv", "Dato3.csv"]
        new_item = random.choice(fake_files)
        
        # Chiede al modello di aggiungere i dati
        self.model.add_item(new_item)