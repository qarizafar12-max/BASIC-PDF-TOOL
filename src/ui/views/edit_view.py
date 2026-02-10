from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                                 QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QFrame, QScrollArea)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QImage, QColor
import fitz # PyMuPDF
from core.pdf_processor import PDFProcessor
import os

class EditView(QWidget):
    def __init__(self):
        super().__init__()
        self.current_pdf = None
        self.page_count = 0
        
        # Actions
        self.pending_rotations = {} # original_idx -> angle
        self.pending_deletes = set() # original_indices
        self.page_order = [] # list of original_indices
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QHBoxLayout()
        header.setContentsMargins(20, 20, 20, 10)
        
        lbl = QLabel("PDF Editor")
        lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        header.addWidget(lbl)
        
        header.addStretch()
        
        btn_open = QPushButton("Open PDF")
        btn_open.setProperty("class", "PrimaryButton")
        btn_open.clicked.connect(self.open_pdf)
        header.addWidget(btn_open)
        
        btn_save = QPushButton("Save Changes")
        btn_save.setProperty("class", "PrimaryButton")
        btn_save.setStyleSheet("background-color: #28a745;")
        btn_save.clicked.connect(self.save_pdf)
        header.addWidget(btn_save)
        
        layout.addLayout(header)
        
        # Main Content
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 0, 20, 20)
        
        # Left: Pages List
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(100, 140))
        self.list_widget.setSpacing(10)
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setResizeMode(QListWidget.Adjust)
        self.list_widget.setDragDropMode(QListWidget.InternalMove) # Enable Drag Drop Reorder!
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: #1A1A1A;
                border: 1px solid #333;
                border-radius: 8px;
            }
            QListWidget::item {
                background: #252525;
                border-radius: 6px;
                padding: 10px;
                color: white;
            }
            QListWidget::item:selected {
                background: #3E7BFA;
            }
        """)
        main_layout.addWidget(self.list_widget, stretch=2)
        
        # Right: Actions Panel
        self.action_panel = QFrame()
        self.action_panel.setFixedWidth(250)
        self.action_panel.setStyleSheet("background: #1A1A1A; border-radius: 8px; padding: 15px;")
        p_layout = QVBoxLayout(self.action_panel)
        p_layout.setSpacing(15)
        
        p_layout.addWidget(QLabel("Page Actions"))
        
        # Rotate
        btn_rot_l = QPushButton("Rotate Left 90°")
        btn_rot_l.setProperty("class", "NavButton")
        btn_rot_l.clicked.connect(lambda: self.rotate_selection(-90))
        p_layout.addWidget(btn_rot_l)
        
        btn_rot_r = QPushButton("Rotate Right 90°")
        btn_rot_r.setProperty("class", "NavButton")
        btn_rot_r.clicked.connect(lambda: self.rotate_selection(90))
        p_layout.addWidget(btn_rot_r)
        
        # Delete
        btn_del = QPushButton("Delete Page")
        btn_del.setStyleSheet("background-color: #FF4444; color: white; border-radius: 6px; padding: 10px;")
        btn_del.clicked.connect(self.delete_selection)
        p_layout.addWidget(btn_del)
        
        p_layout.addSpacing(10)
        p_layout.addWidget(QLabel("Tip: Drag pages to reorder!"))
        
        p_layout.addSpacing(20)
        p_layout.addWidget(QLabel("Content Actions"))
        
        btn_text = QPushButton("Add Text")
        btn_text.setProperty("class", "NavButton")
        btn_text.setStyleSheet("background-color: #9C27B0;")
        btn_text.clicked.connect(self.add_text_dialog)
        p_layout.addWidget(btn_text)
        
        p_layout.addStretch()
        
        main_layout.addWidget(self.action_panel)
        layout.addLayout(main_layout)

    def open_pdf(self):
        f, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if f:
            self.current_pdf = f
            self.load_pages(f)

    def load_pages(self, path):
        self.list_widget.clear()
        self.pending_rotations = {}
        self.pending_deletes = set()
        
        doc = fitz.open(path)
        self.page_count = len(doc)
        
        # Initialize default order [0, 1, 2...]
        self.page_order = list(range(len(doc)))
        
        for i in range(len(doc)):
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2)) 
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            qpix = QPixmap.fromImage(img)
            
            item = QListWidgetItem(f"Page {i+1}")
            item.setIcon(QIcon(qpix))
            item.setData(Qt.UserRole, i) # Store ORIGINAL index
            self.list_widget.addItem(item)
            
        doc.close()

    def rotate_selection(self, angle):
        items = self.list_widget.selectedItems()
        if not items: return
        
        for item in items:
            orig_idx = item.data(Qt.UserRole)
            curr = self.pending_rotations.get(orig_idx, 0)
            self.pending_rotations[orig_idx] = curr + angle
            item.setText(f"Page {orig_idx+1} (Rot {self.pending_rotations[orig_idx]}°)")

    def delete_selection(self):
        items = self.list_widget.selectedItems()
        if not items: return
        
        for item in items:
            orig_idx = item.data(Qt.UserRole)
            self.pending_deletes.add(orig_idx)
            row = self.list_widget.row(item)
            self.list_widget.takeItem(row)

    def add_text_dialog(self):
        items = self.list_widget.selectedItems()
        if not items:
            QMessageBox.warning(self, "Warning", "Select a page to add text to.")
            return
            
        from PySide6.QtWidgets import QInputDialog, QDialog, QFormLayout, QLineEdit, QComboBox, QHBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Text")
        form = QFormLayout(dialog)
        
        txt_input = QLineEdit()
        form.addRow("Text:", txt_input)
        
        pos_input = QComboBox()
        pos_input.addItems(["Header (Top-Left)", "Header (Top-Right)", "Center", "Footer (Bottom-Left)", "Footer (Bottom-Right)"])
        form.addRow("Position:", pos_input)
        
        btn_box = QHBoxLayout()
        ok_btn = QPushButton("Add")
        ok_btn.clicked.connect(dialog.accept)
        btn_box.addWidget(ok_btn)
        form.addRow(btn_box)
        
        if dialog.exec():
             text = txt_input.text()
             pos = pos_input.currentText()
             if not text: return
             
             orig_idx = items[0].data(Qt.UserRole)
             
             # Coords (Assuming approx 72 DPI, A4 ~ 595x842)
             x, y = 50, 50
             if "Top-Right" in pos: x = 400
             if "Center" in pos: x, y = 250, 400
             if "Footer" in pos: y = 750
             if "Bottom-Right" in pos: x, y = 400, 780
             
             # Queue Action for Backend
             # We need to store this separately or integrate into save_pdf logic.
             # Current save_pdf rebuilds actions list. We need a way to persist these text actions.
             # Let's add a list for text_actions.
             if not hasattr(self, 'text_actions'): self.text_actions = []
             
             self.text_actions.append({
                 "type": "add_text", 
                 "page": orig_idx, 
                 "text": text,
                 "x": x, "y": y,
                 "fontsize": 12,
                 "color": (0, 0, 0)
             })
             
             items[0].setText(f"Page {orig_idx+1} (+Text)")

    def save_pdf(self):
        if not self.current_pdf: return
        
        # Calculate current order from List Widget (handles Drag & Drop moves)
        final_order_actions = [] 
        
        # We need to construct the 'actions' list for pdf_processor
        # Logic: 
        # 1. 'move' is implicitly handled by the order of items in list_widget
        # 2. 'rotate' is mapped by orig_idx
        # 3. 'delete' is pages NOT in list_widget (or tracked in set)
        
        # Actually, our pdf_processor's 'modify_pdf' expects a list of operations including 'move' from src to dst.
        # But since we have the FINAL desired order, it's easier to rewrite modification logic to accept "pages_list".
        # Let's adjust the backend to be smarter or map this to moves.
        
        # EASIER: Send a 'reorder' action with the full list of indices.
        
        current_indices = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            current_indices.append(item.data(Qt.UserRole))
            
        # Construct actions
        actions = []
        
        # Rotations
        for idx, angle in self.pending_rotations.items():
            actions.append({"type": "rotate", "page": idx, "angle": angle})
            
        # Add Text Actions (if any)
        if hasattr(self, 'text_actions'):
            actions.extend(self.text_actions)
            
        # We need to tell backend the NEW order.
        actions.append({"type": "set_order", "order": current_indices})
        
        out, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if out:
            success, msg = PDFProcessor.modify_pdf(self.current_pdf, out, actions)
            if success:
                QMessageBox.information(self, "Success", "PDF Saved!")
                self.load_pages(out) # Reload
                # Clear text actions
                self.text_actions = []
            else:
                QMessageBox.critical(self, "Error", msg)
