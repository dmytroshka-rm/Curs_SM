import sys
import os

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)  
project_root = os.path.dirname(current_dir) 

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSettings
from frontend.windows.main_window import MainWindow
from frontend.theme import apply_theme, current_theme


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SmartHome Energy Manager")
    # Set application icon
    icon_path = os.path.join(project_root, 'frontend', 'resources', 'icons', 'app.svg')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Apply previously selected theme (default: light)
    apply_theme(current_theme())

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

