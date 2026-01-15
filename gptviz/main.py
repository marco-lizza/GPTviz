import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from .model.app_model import AppModel
from .view.main_window import MainWindow
from .controller.app_controller import AppController

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Percorso assoluto all’icona
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "assets", "icon.png")

    app.setWindowIcon(QIcon(icon_path))

    model = AppModel()
    view = MainWindow()
    controller = AppController(model, view)

    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
