class Sidebar_controller:
    def __init__(self, model, sidebar_view):
        self.model = model
        self.sidebar_view = sidebar_view

        self.set_up_binding()

    def set_up_binding(self):
        self.sidebar_view.process_requested.connect(self.handle_process)
        self.model.data_changed.connect(self.sidebar_view.update_sidebar)

    def handle_import(self):
        import random
        fake_files = ["Dato1.csv", "Dato2.csv", "Dato3.csv"]
        new_item = random.choice(fake_files)
        
        # Chiede al modello di aggiungere i dati
        self.model.add_item(new_item)

    def handle_process(self, item_name):
        self.model.perform_operation(item_name)