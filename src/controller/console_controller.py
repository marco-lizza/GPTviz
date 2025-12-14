class Console_controller:
    def __init__(self, model, console_view):
        self.model = model
        self.console_view = console_view

        self.set_up_binding()

    def set_up_binding(self):
        self.model.log_message.connect(self.update_console)
        self.model.erase_console.connect(self.console_view.clear_console)

    def update_console(self, message: str):
        self.console_view.append_log(message)
