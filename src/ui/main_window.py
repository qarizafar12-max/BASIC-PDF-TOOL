from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QFrame, QLabel, QSizeGrip
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from PySide6.QtGui import QIcon
import qtawesome as qta

from ui.views.home_view import HomeView
from ui.views.create_view import CreateView
from ui.views.tools_view import ToolsView
from ui.views.text_view import TextView
from ui.views.file_view import FileView
from ui.views.qr_view import QRView
from ui.views.info_view import InfoView

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QFrame, QLabel, QSizeGrip, QButtonGroup
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from PySide6.QtGui import QIcon
import qtawesome as qta

from ui.views.home_view import HomeView
from ui.views.create_view import CreateView
from ui.views.tools_view import ToolsView
from ui.views.text_view import TextView
from ui.views.file_view import FileView
from ui.views.qr_view import QRView
from ui.views.info_view import InfoView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced PDF Tool - Premium Edition")
        self.resize(1200, 800)
        
        # Set Window Icon
        try:
            from PySide6.QtGui import QIcon
            self.setWindowIcon(QIcon("src/assets/excode_icon.png"))
        except:
            pass

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 1. Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(260)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(10, 20, 10, 20)
        self.sidebar_layout.setSpacing(8)
        
        # Top Bar (Toggle + Logo)
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(5, 0, 5, 20)
        
        self.btn_toggle = QPushButton()
        self.btn_toggle.setObjectName("ToggleBtn")
        self.btn_toggle.setIcon(qta.icon("fa5s.bars", color="#E0E0E0"))
        self.btn_toggle.setIconSize(QSize(20, 20))
        self.btn_toggle.setFixedSize(32, 32)
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.toggle_sidebar)
        top_bar.addWidget(self.btn_toggle)
        
        self.logo = QLabel("PDF TOOL")
        self.logo.setObjectName("LogoLabel")
        top_bar.addWidget(self.logo)
        top_bar.addStretch()
        
        self.sidebar_layout.addLayout(top_bar)
        
        # Nav Group (Exclusivity)
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        
        # Nav Buttons (Icon + Text)
        self.nav_buttons = []
        self.add_nav_btn("Dashboard", "home", "fa5s.home")
        self.add_nav_btn("Create PDF", "create", "fa5s.plus-square")
        self.add_nav_btn("PDF Tools", "merge", "fa5s.layer-group")
        self.add_nav_btn("Text & OCR", "text", "fa5s.font")
        self.add_nav_btn("File Manager", "file", "fa5s.folder-open")
        self.add_nav_btn("QR Code", "qr", "fa5s.qrcode")
        
        self.sidebar_layout.addStretch()
        
        # Bottom Actions
        self.add_nav_btn("Premium / About", "info", "fa5s.crown")
        
        # Add Sidebar to Main Layout
        self.main_layout.addWidget(self.sidebar)
        
        # 2. Content Area
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack)
        
        # Views
        self.views = {}
        self.init_views()
        
        # Styles
        with open("src/ui/styles.qss", "r") as f:
            self.setStyleSheet(f.read())
            
        # Select Home initially
        if self.nav_buttons:
            self.navigate("home", self.nav_buttons[0][0])

    def add_nav_btn(self, text, route, icon_name):
        btn = QPushButton(text)
        btn.setProperty("class", "NavButton")
        btn.setCheckable(True)
        try:
            btn.setIcon(qta.icon(icon_name, color="#909090"))
        except:
             pass
        btn.setIconSize(QSize(20, 20))
        btn.clicked.connect(lambda: self.navigate(route, btn))
        
        self.sidebar_layout.addWidget(btn)
        self.nav_group.addButton(btn)
        self.nav_buttons.append((btn, route, icon_name, text)) 

    def toggle_sidebar(self):
        width = self.sidebar.width()
        collapsed_width = 70
        expanded_width = 260
        
        target_width = expanded_width if width == collapsed_width else collapsed_width
        
        self.anim = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.anim.setDuration(400)
        self.anim.setStartValue(width)
        self.anim.setEndValue(target_width)
        self.anim.setEasingCurve(QEasingCurve.InOutQuart)
        
        self.anim_max = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.anim_max.setDuration(400)
        self.anim_max.setStartValue(width)
        self.anim_max.setEndValue(target_width)
        self.anim_max.setEasingCurve(QEasingCurve.InOutQuart)
        
        self.group = QParallelAnimationGroup()
        self.group.addAnimation(self.anim)
        self.group.addAnimation(self.anim_max)
        self.group.start()
        
        # Update UI Elements based on state
        is_collapsing = target_width == collapsed_width
        self.logo.setVisible(not is_collapsing)
        
        for btn, route, icon_name, text in self.nav_buttons:
            if is_collapsing:
                btn.setText("") # Hide text
                btn.setStyleSheet("text-align: center; padding: 12px 0;") # Center icon
                btn.setToolTip(text)
            else:
                btn.setText(text)
                btn.setStyleSheet("") # Revert to .qss default (left aligned)
                btn.setToolTip("")

    def init_views(self):
        self.home_view = HomeView(self.navigate)
        self.content_stack.addWidget(self.home_view)
        self.views["home"] = self.home_view
        
        self.create_view = CreateView()
        self.content_stack.addWidget(self.create_view)
        self.views["create"] = self.create_view
        
        self.tools_view = ToolsView()
        self.content_stack.addWidget(self.tools_view)
        self.views["merge"] = self.tools_view
        self.views["split"] = self.tools_view
        self.views["compress"] = self.tools_view
        
        self.text_view = TextView()
        self.content_stack.addWidget(self.text_view)
        self.views["text"] = self.text_view

        self.file_view = FileView()
        self.content_stack.addWidget(self.file_view)
        self.views["file"] = self.file_view
        
        self.qr_view = QRView()
        self.content_stack.addWidget(self.qr_view)
        self.views["qr"] = self.qr_view
        
        self.info_view = InfoView()
        self.content_stack.addWidget(self.info_view)
        self.views["info"] = self.info_view

    def navigate(self, route, sender_btn=None):
        # Update Button States (Visuals)
        # Note: QButtonGroup handles the checked state logic (exclusivity) automatically if buttons are clicked.
        # But if we navigate programmatically (e.g. from Home), we must check manually.
        
        target_btn = sender_btn
        
        # Resolve target button if not explicit or if navigating to sub-route
        if not target_btn:
            for btn, r, _, _ in self.nav_buttons:
                mapped = r
                if route in ["split", "compress"]: mapped = "merge"
                
                if r == mapped or (route in ["split", "compress"] and r == "merge"):
                    target_btn = btn
                    break

        # Apply Visual Updates (Icons)
        if target_btn:
            target_btn.setChecked(True)
            for btn, _, icon, _ in self.nav_buttons:
                color = "#FFFFFF" if btn == target_btn else "#909090"
                btn.setIcon(qta.icon(icon, color=color))

        # Switch Switch View
        if route in self.views:
            self.content_stack.setCurrentWidget(self.views[route])
            
            # Handle Tab Switching in Tools View
            if route == "merge" and hasattr(self.views[route], "set_current_tab"):
                 self.views[route].set_current_tab(0)
            elif route == "split" and hasattr(self.views[route], "set_current_tab"):
                 self.views[route].set_current_tab(1)
            elif route == "compress" and hasattr(self.views[route], "set_current_tab"):
                 self.views[route].set_current_tab(2)


