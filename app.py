import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import PyOPLMainWindow
from qt_material import apply_stylesheet

def main():
    app = QApplication(sys.argv)
    
    # Aplica o tema dark_amber para um visual gamer/premium
    apply_stylesheet(app, theme='dark_amber.xml')
    
    window = PyOPLMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
