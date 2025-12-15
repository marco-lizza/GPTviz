class Toolbar_controller:
    def __init__(self, model, toolbar_view):
        self.model = model
        self.toolbar_view = toolbar_view

        self.set_up_binding()

    def set_up_binding(self):
        self.toolbar_view.load_file_names.connect(self.handle_load_file_names)

    def handle_load_file_names(self):
        self.model.load_file_names()