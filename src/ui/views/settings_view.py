from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                                 QComboBox, QFrame, QMessageBox)
from PySide6.QtCore import Qt

class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        layout.addSpacing(30)
        
        # Theme Section
        theme_frame = QFrame()
        theme_frame.setStyleSheet("background: #1A1A1A; border-radius: 8px; padding: 20px;")
        t_layout = QVBoxLayout(theme_frame)
        
        t_lbl = QLabel("Appearance")
        t_lbl.setStyleSheet("font-size: 18px; font-weight: bold;")
        t_layout.addWidget(t_lbl)
        
        t_layout.addSpacing(10)
        
        row = QHBoxLayout()
        row.addWidget(QLabel("App Theme:"))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark (Default)", "Light", "High Contrast"])
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        row.addWidget(self.theme_combo)
        
        row.addStretch()
        t_layout.addLayout(row)
        
        layout.addWidget(theme_frame)
        layout.addStretch()

    def change_theme(self, index):
        # We can swap QSS content here
        main_window = self.window()
        if not main_window: return
        
        theme = self.theme_combo.currentText()
        
        if theme == "Light":
            # Simple Light QSS
            qss = """
            QMainWindow { background-color: #F0F0F0; }
            QWidget { color: #333; font-family: "Segoe UI"; }
            QFrame#Sidebar { background-color: #E0E0E0; border-right: 1px solid #CCC; }
            QPushButton { background: #DDD; color: #333; border: none; padding: 10px; border-radius: 4px; }
            QPushButton:hover { background: #CCC; }
            QLabel { color: #333; }
            QTextEdit { background: white; color: black; }
            QListWidget { background: white; color: black; border: 1px solid #DDD; }
            """
        elif theme == "High Contrast":
             qss = """
            QMainWindow { background-color: black; }
            QWidget { color: yellow; font-family: "Consolas"; font-weight: bold; }
            QFrame#Sidebar { background-color: black; border-right: 2px solid yellow; }
            QPushButton { background: black; color: yellow; border: 2px solid yellow; padding: 10px; }
            QPushButton:hover { background: yellow; color: black; }
             """
        else:
            # Load default from file
            try:
                with open("src/ui/styles.qss", "r") as f:
                    qss = f.read()
            except:
                qss = ""
                
        main_window.setStyleSheet(qss)
