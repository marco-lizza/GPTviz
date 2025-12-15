class Attention_navigator_controller:

    def __init__(self, model, attention_navigator_view):
        self.model = model
        self.attention_navigator_view = attention_navigator_view

        self.set_up_binding()

    def set_up_binding(self):
        self.model.attentions_loaded.connect(self.update_attention_navigator)

    def update_attention_navigator(self,attention_metadata):
        self.attention_navigator_view.update_sidebar(attention_metadata[0],attention_metadata[1],attention_metadata[2])

