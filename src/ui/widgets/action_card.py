from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
from PySide6.QtGui import QColor, QCursor
import qtawesome as qta

class ActionCard(QFrame):
    def __init__(self, title, desc, icon_name, on_click, parent=None):
        super().__init__(parent)
        self.on_click = on_click
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setProperty("class", "ActionCard")
        self.setFixedHeight(180) # Slightly taller for better spacing
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Icon
        self.icon_lbl = QLabel()
        # Use qtawesome to generate a pixmap
        icon = qta.icon(f"fa5s.{icon_name}", color="#3E7BFA")
        self.icon_lbl.setPixmap(icon.pixmap(40, 40))
        self.icon_lbl.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.icon_lbl)
        
        # Title
        self.title_lbl = QLabel(title)
        self.title_lbl.setProperty("class", "CardTitle")
        layout.addWidget(self.title_lbl)
        
        # Desc
        self.desc_lbl = QLabel(desc)
        self.desc_lbl.setProperty("class", "CardDesc")
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self.desc_lbl)
        
        layout.addStretch()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.on_click()
