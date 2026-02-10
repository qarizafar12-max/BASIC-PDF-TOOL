from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from ui.widgets.action_card import ActionCard

class HomeView(QWidget):
    def __init__(self, navigation_callback):
        super().__init__()
        self.nav = navigation_callback
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Header
        welcome = QLabel("Welcome Back")
        welcome.setObjectName("WelcomeTitle")
        layout.addWidget(welcome)
        
        sub = QLabel("What would you like to do today?")
        sub.setObjectName("WelcomeSub")
        layout.addWidget(sub)
        
        layout.addSpacing(20)
        
        # Grid for Cards
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # Cards
        # Row 0
        grid.addWidget(ActionCard("Create PDF", "Create PDF from Images", "plus-square", lambda: self.nav("create")), 0, 0)
        grid.addWidget(ActionCard("Merge/Split", "PDF Operations", "layer-group", lambda: self.nav("merge")), 0, 1)
        grid.addWidget(ActionCard("OCR Tool", "Extract Text from Images/PDF", "font", lambda: self.nav("text")), 0, 2)
        
        # Row 1
        grid.addWidget(ActionCard("File Tools", "Rename, Zip, Organize", "folder-open", lambda: self.nav("file")), 1, 0)
        grid.addWidget(ActionCard("Word Count", "Count Words/Chars", "align-left", lambda: self.nav("text")), 1, 1)
        grid.addWidget(ActionCard("QR Generator", "Create QR Codes", "qrcode", lambda: self.nav("qr")), 1, 2)

        layout.addLayout(grid)
        layout.addStretch()

