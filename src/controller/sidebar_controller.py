class Sidebar_controller:
    def __init__(self, model, sidebar_view):
        self.model = model
        self.sidebar_view = sidebar_view

        self.set_up_binding()

    def set_up_binding(self):
        self.sidebar_view.file_clicked.connect(self.handle_file_clicked)
        self.model.file_name_loaded.connect(self.sidebar_view.update_sidebar)

    def handle_file_clicked(self, item_name):
        self.model.load_file(item_name)