from PyQt6.QtCore import QObject, pyqtSignal
from .data.attention_loader import Attention_loader
import torch

class AppModel(QObject):

    base_path="workspace"

    file_name_loaded = pyqtSignal(list)   
    log_message = pyqtSignal(str) 
    erase_console=pyqtSignal()
    attentions_loaded = pyqtSignal(list) 
    open_options = pyqtSignal() 
    head_matrix_loaded=pyqtSignal(torch.Tensor)
    clear_workspace=pyqtSignal()

    def __init__(self):
        super().__init__()
        self.actual_attentions = None

    def load_file_names(self):
        loader = Attention_loader(self.base_path) 
        try:
            names = loader.list_files()
            self.log_message.emit(f"File json presenti nella cartella Workspace caricati")
            self.file_name_loaded.emit(names)

        except Exception as e:
            self.log_message.emit(e)

    def load_file(self, file_name):
        loader = Attention_loader(self.base_path) 
        try:
            self.log_message.emit(f"Caricamento file: {self.base_path}/{file_name}")
            self.actual_attentions = loader.load(file_name)
            self.attentions_loaded.emit(self.actual_attentions.get_metadata())
            self.log_message.emit("Caricamento file completato")
            self.log_message.emit(self.actual_attentions.info())
            self.clear_workspace.emit()
        except Exception as e:
            self.log_message.emit(e)

    def get_head(self,iter_idx, lev_idx, head_idx):
        self.head_matrix_loaded.emit(self.actual_attentions.get_matrix(iter_idx, lev_idx, head_idx))
        
    def open_option(self):
        self.open_options.emit()

    def clear_console(self):
        #.... logica legata a una classe console da creare 
        self.erase_console.emit()