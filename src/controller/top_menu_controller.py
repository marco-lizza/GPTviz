class Top_menu_controller:
    def __init__(self, model, top_menu_view):
        self.model = model
        self.top_menu_view = top_menu_view

        self.set_up_binding()

    def set_up_binding(self):
        self.top_menu_view.open_options.connect(self.open_options)
        self.top_menu_view.clear_console.connect(self.clear_console)

    def open_options(self):
        self.model.open_option()

    def clear_console(self):
        self.model.clear_console()