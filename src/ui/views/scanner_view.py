from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                                 QFileDialog, QTextEdit, QSplitter, QFrame, QMessageBox)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QImage
from core.pdf_processor import PDFProcessor
import os

class ScannerView(QWidget):
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background: #1A1A1A; border-bottom: 1px solid #333;")
        header = QHBoxLayout(header_frame)
        
        title = QLabel("AI Scanner (OCR)")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header.addWidget(title)
        
        header.addStretch()
        
        btn_load = QPushButton("Load Image")
        btn_load.setProperty("class", "PrimaryButton")
        btn_load.clicked.connect(self.load_image)
        header.addWidget(btn_load)
        
        btn_scan = QPushButton("Extract Text")
        btn_scan.setProperty("class", "PrimaryButton")
        btn_scan.setStyleSheet("background-color: #9C27B0;") # Purple for AI
        btn_scan.clicked.connect(self.perform_ocr)
        header.addWidget(btn_scan)
        
        layout.addWidget(header_frame)
        
        # Splitter Content
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle { background: #333; width: 2px; }
        """)
        
        # Left: Image Preview
        self.preview_lbl = QLabel("No Image Selected")
        self.preview_lbl.setAlignment(Qt.AlignCenter)
        self.preview_lbl.setStyleSheet("background: #111; color: #555; font-size: 16px;")
        self.preview_lbl.setMinimumWidth(400)
        splitter.addWidget(self.preview_lbl)
        
        # Right: Text Output
        self.text_out = QTextEdit()
        self.text_out.setPlaceholderText("Extracted text will appear here...")
        self.text_out.setStyleSheet("""
            QTextEdit {
                background: #151515;
                color: #DDD;
                border: none;
                padding: 15px;
                font-family: Consolas, monospace;
                font-size: 14px;
            }
        """)
        splitter.addWidget(self.text_out)
        
        # Equal sizes
        splitter.setSizes([600, 600])
        
        layout.addWidget(splitter)

    def load_image(self):
        f, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.tiff)")
        if f:
            self.current_image_path = f
            self.show_preview(f)
            self.text_out.clear()

    def show_preview(self, path):
        pix = QPixmap(path)
        if pix.isNull():
             self.preview_lbl.setText("Failed to load image.")
             return
             
        # Scale to fit (simple)
        scaled = pix.scaled(self.preview_lbl.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_lbl.setPixmap(scaled)

    def resizeEvent(self, event):
        # Re-scale preview on resize if image exists
        if self.current_image_path:
             self.show_preview(self.current_image_path)
        super().resizeEvent(event)

    def perform_ocr(self):
        if not self.current_image_path:
            QMessageBox.warning(self, "Warning", "Please load an image first.")
            return

        self.text_out.setText("Scanning... please wait...")
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        
        success, text = PDFProcessor.extract_text_from_image(self.current_image_path)
        
        if success:
            self.text_out.setText(text)
        else:
            self.text_out.setText(f"Error: {text}")
            QMessageBox.critical(self, "Error", f"Failed to extract text.\n{text}")
