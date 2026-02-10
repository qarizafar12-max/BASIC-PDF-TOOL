import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.startup import StartupScreen

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    
    # Show Splash
    splash = StartupScreen()
    
    # Store window in a mutable object (list) to access it in nested function
    main_window_container = []

    def show_main():
        window = MainWindow()
        window.show()
        main_window_container.append(window)

    splash.finished.connect(show_main)
    splash.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
