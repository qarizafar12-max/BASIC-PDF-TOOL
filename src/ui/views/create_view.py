from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QFrame, QProgressBar
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from core.pdf_processor import PDFProcessor
import os

class CreateView(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_files = []
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        header = QLabel("Create PDF from Images")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.btn_add = QPushButton("+ Add Images")
        self.btn_add.setProperty("class", "PrimaryButton")
        self.btn_add.clicked.connect(self.add_images)
        toolbar.addWidget(self.btn_add)
        
        self.btn_clear = QPushButton("Clear All")
        self.btn_clear.setStyleSheet("background: transparent; color: #FF5555; border: 1px solid #FF5555; border-radius: 6px; padding: 8px;")
        self.btn_clear.clicked.connect(self.clear_list)
        toolbar.addWidget(self.btn_clear)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # File List
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #1A1A1A;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 10px;
                color: white;
            }
            QListWidget::item {
                padding: 10px;
                background-color: #222222;
                margin-bottom: 5px;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.file_list)
        
        # Footer
        footer = QHBoxLayout()
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color: #AAAAAA;")
        footer.addWidget(self.status_lbl)
        
        footer.addStretch()
        
        self.btn_convert = QPushButton("Convert to PDF")
        self.btn_convert.setProperty("class", "PrimaryButton")
        self.btn_convert.setStyleSheet("background-color: #28a745;") # Green override
        self.btn_convert.clicked.connect(self.convert_files)
        footer.addWidget(self.btn_convert)
        
        layout.addLayout(footer)

    def add_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.jpg *.jpeg *.png *.bmp *.webp)")
        if files:
            self.selected_files.extend(files)
            self.update_list()

    def update_list(self):
        self.file_list.clear()
        for f in self.selected_files:
            item = QListWidgetItem(os.path.basename(f))
            item.setIcon(QIcon.fromTheme("image-x-generic")) # Try system icon
            self.file_list.addItem(item)
            
    def clear_list(self):
        self.selected_files = []
        self.update_list()

    def convert_files(self):
        if not self.selected_files:
            QMessageBox.warning(self, "No Images", "Please add at least one image.")
            return
            
        out_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if out_path:
            self.status_lbl.setText("Converting...")
            self.btn_convert.setEnabled(False)
            
            # Using QCoreApplication.processEvents() to allow UI update if this was sync
            # Ideally this runs in a thread. For now, simple sync.
            from PySide6.QtWidgets import QApplication
            QApplication.processEvents()
            
            success, msg = PDFProcessor.create_from_images(self.selected_files, out_path)
            
            self.status_lbl.setText(msg)
            self.btn_convert.setEnabled(True)
            
            if success:
                QMessageBox.information(self, "Success", "PDF Created Successfully!")
            else:
                QMessageBox.critical(self, "Error", msg)
