class Workspace_controller:
    def __init__(self, model, workspace_view):
        self.model = model
        self.workspace_view = workspace_view

        self.set_up_binding()

    def set_up_binding(self):
        self.model.processing_done.connect(self.update_workspace)

    def update_workspace(self, result_text: str):
        self.workspace_view.show_result(result_text)