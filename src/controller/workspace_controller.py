class Workspace_controller:
    def __init__(self, model, workspace_view):
        self.model = model
        self.workspace_view = workspace_view

        self.set_up_binding()

    def set_up_binding(self):
       self.model.head_matrix_loaded.connect(self.workspace_view.visualize_attentions_matrix)
       self.model.clear_workspace.connect(self.workspace_view.reset_view)