from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                                 QFileDialog, QMessageBox, QTabWidget, QTextEdit, QFrame, QProgressDialog, QComboBox)
from PySide6.QtCore import Qt, QThread, Signal
from core.pdf_processor import PDFProcessor
import os

class TextExtractionThread(QThread):
    finished = Signal(bool, str)
    progress = Signal(str)
    
    def __init__(self, path):
        super().__init__()
        self.path = path
    
    def run(self):
        try:
            self.progress.emit("Extracting...")
            def cb(msg): self.progress.emit(msg)
            
            # Simple check extension
            ext = os.path.splitext(self.path)[1].lower()
            if ext == '.pdf':
                success, text = PDFProcessor.extract_text(self.path, progress_callback=cb)
            elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.webp']:
                success, text = PDFProcessor.extract_text_from_image(self.path)
            else:
                success, text = False, "Unsupported file type"
                
            self.finished.emit(success, text)
        except Exception as e:
            self.finished.emit(False, str(e))

class TextView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        self.init_ocr_tab()
        self.init_word_count_tab()
        
        layout.addWidget(self.tabs)

    def init_ocr_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # File Select
        hbox = QHBoxLayout()
        self.lbl_ocr_file = QLabel("No file selected")
        self.lbl_ocr_file.setStyleSheet("color: #909090; font-style: italic;")
        hbox.addWidget(self.lbl_ocr_file)
        
        btn_sel = QPushButton("Select Image/PDF")
        btn_sel.setProperty("class", "SecondaryButton")
        btn_sel.clicked.connect(self.select_ocr_file)
        hbox.addWidget(btn_sel)
        layout.addLayout(hbox)
        
        layout.addSpacing(20)
        
        # Output
        self.txt_ocr_out = QTextEdit()
        self.txt_ocr_out.setPlaceholderText("Extracted text will appear here...")
        # Stylesheet handles QTextEdit generally, or we can add specific ID if needed
        layout.addWidget(self.txt_ocr_out)
        
        # Actions
        act_box = QHBoxLayout()
        act_box.addStretch()
        
        btn_run = QPushButton("Extract Text")
        btn_run.setProperty("class", "PrimaryButton")
        btn_run.clicked.connect(self.run_ocr)
        act_box.addWidget(btn_run)
        
        btn_save = QPushButton("Save to File")
        btn_save.setProperty("class", "SecondaryButton")
        btn_save.clicked.connect(self.save_ocr)
        act_box.addWidget(btn_save)
        
        layout.addLayout(act_box)
        self.tabs.addTab(tab, "OCR Extractor")

    def select_ocr_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select File", "", "Files (*.pdf *.png *.jpg *.jpeg *.bmp *.webp)")
        if f:
            self.ocr_file = f
            self.lbl_ocr_file.setText(os.path.basename(f))
            self.lbl_ocr_file.setStyleSheet("color: white;")

    def run_ocr(self):
        if not hasattr(self, 'ocr_file'): return
        
        self.pd = QProgressDialog("Processing...", "Cancel", 0, 0, self)
        self.pd.setWindowModality(Qt.WindowModality.WindowModal)
        self.pd.show()
        
        self.ocr_thread = TextExtractionThread(self.ocr_file)
        self.ocr_thread.progress.connect(self.pd.setLabelText)
        self.ocr_thread.finished.connect(self.on_ocr_finish)
        self.ocr_thread.start()
        
    def on_ocr_finish(self, success, text):
        self.pd.close()
        if success:
            self.txt_ocr_out.setPlainText(text)
            QMessageBox.information(self, "Success", "Text extracted.")
        else:
            QMessageBox.critical(self, "Error", text)

    def save_ocr(self):
        text = self.txt_ocr_out.toPlainText()
        if not text: return
        
        path, _ = QFileDialog.getSaveFileName(self, "Save Text", "", "Text Files (*.txt)")
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)

    def init_word_count_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(40, 40, 40, 40)
        
        layout.addWidget(QLabel("Paste text or select file to count:"))
        
        self.txt_count_in = QTextEdit()
        # Stylesheet handles general QTextEdit styling
        self.txt_count_in.textChanged.connect(self.update_count)
        layout.addWidget(self.txt_count_in)
        
        btn_load = QPushButton("Load Text File")
        btn_load.setProperty("class", "SecondaryButton")
        btn_load.clicked.connect(self.load_count_file)
        layout.addWidget(btn_load)
        
        layout.addSpacing(20)
        
        # Stats
        stats_frame = QFrame()
        stats_frame.setProperty("class", "ActionCard")
        s_layout = QHBoxLayout(stats_frame)
        
        self.lbl_words = QLabel("Words: 0")
        self.lbl_chars = QLabel("Chars: 0")
        self.lbl_lines = QLabel("Lines: 0")
        
        for l in [self.lbl_words, self.lbl_chars, self.lbl_lines]:
            l.setStyleSheet("color: white; font-weight: bold; font-size: 14px; background: transparent;")
            s_layout.addWidget(l)
            
        layout.addWidget(stats_frame)
        self.tabs.addTab(tab, "Word Counter")

    def load_count_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select Text File", "", "Text Files (*.txt *.md *.py *.json)")
        if f:
            try:
                with open(f, 'r', encoding='utf-8') as fi:
                    self.txt_count_in.setPlainText(fi.read())
            except:
                QMessageBox.warning(self, "Error", "Could not read file.")

    def update_count(self):
        text = self.txt_count_in.toPlainText()
        
        words = len(text.split())
        chars = len(text)
        lines = len(text.splitlines()) if text else 0
        
        self.lbl_words.setText(f"Words: {words}")
        self.lbl_chars.setText(f"Chars: {chars}")
        self.lbl_lines.setText(f"Lines: {lines}")
