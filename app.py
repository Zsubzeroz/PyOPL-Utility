import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import PyOPLMainWindow

def main():
    app = QApplication(sys.argv)
    
    # Utiliza o estilo Fusion para um visual limpo e consistente no Linux
    app.setStyle("Fusion")
    
    window = PyOPLMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
