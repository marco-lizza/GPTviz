from .top_menu_controller import Top_menu_controller
from .toolbar_controller import Toolbar_controller
from .sidebar_controller import Sidebar_controller
from .console_controller import Console_controller
from .workspace_controller import Workspace_controller
from .attention_navigator_controller import Attention_navigator_controller

class AppController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.top_menu_ctrl=Top_menu_controller(model,view.top_menu)
        self.toolbar_ctrl=Toolbar_controller(model,view.toolbar)
        self.sidebar_ctrl=Sidebar_controller(model,view.sidebar)
        self.console_ctrl=Console_controller(model,view.console)
        self.workspace_ctrl=Workspace_controller(model,view.workspace)
        self.attention_navigator_ctrl=Attention_navigator_controller(model,view.attention_navigator)
        self.set_up_binding()

    def set_up_binding(self):
        self.model.open_options.connect(self.view.open_options_dialog)
