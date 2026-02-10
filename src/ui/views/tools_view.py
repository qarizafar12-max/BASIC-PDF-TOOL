from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                                 QListWidget, QListWidgetItem, QFileDialog, QMessageBox, 
                                 QTabWidget, QLineEdit, QRadioButton, QButtonGroup, QFrame,
                                 QTextEdit, QComboBox, QSpinBox, QCheckBox, QScrollArea, QProgressDialog)
from PySide6.QtCore import Qt, QThread, Signal
from core.pdf_processor import PDFProcessor
from core.ai_processor import AIProcessor, CitationFormat
import os

# Worker thread for text extraction to prevent GUI freezing
class TextExtractionThread(QThread):
    finished = Signal(bool, str)  # success, text
    progress = Signal(str)  # progress message
    
    def __init__(self, pdf_path, page_range=None):
        super().__init__()
        self.pdf_path = pdf_path
        self.page_range = page_range
    
    def run(self):
        try:
            self.progress.emit("Extracting text from PDF...")
            # Define callback wrapper to emit signals
            def progress_callback(msg):
                self.progress.emit(msg)
            
            success, text = PDFProcessor.extract_text(self.pdf_path, self.page_range, progress_callback=progress_callback)
            self.finished.emit(success, text)
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")


class ToolsView(QWidget):
    def __init__(self):
        super().__init__()
        self.merge_files = []
        self.split_file = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Merge Tab
        self.merge_tab = QWidget()
        self.init_merge_tab()
        self.tabs.addTab(self.merge_tab, "Merge PDFs")
        
        # Split Tab
        self.split_tab = QWidget()
        self.init_split_tab()
        self.tabs.addTab(self.split_tab, "Split PDF")
        
        # Compress Tab
        self.compress_tab = QWidget()
        self.init_compress_tab()
        self.tabs.addTab(self.compress_tab, "Compress PDF")

    def set_current_tab(self, index):
        self.tabs.setCurrentIndex(index)

    # ================= MERGE TAB =================
    def init_merge_tab(self):
        layout = QVBoxLayout(self.merge_tab)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Toolbar
        toolbar = QHBoxLayout()
        btn_add = QPushButton("+ Add PDFs")
        btn_add.setProperty("class", "PrimaryButton")
        btn_add.clicked.connect(self.add_pdfs)
        toolbar.addWidget(btn_add)
        
        btn_clear = QPushButton("Clear")
        btn_clear.setProperty("class", "DangerButton")
        btn_clear.clicked.connect(self.clear_pdfs)
        toolbar.addWidget(btn_clear)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # List
        self.pdf_list = QListWidget()
        layout.addWidget(self.pdf_list)
        
        # Action
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        btn_merge = QPushButton("Merge PDFs")
        btn_merge.setProperty("class", "PrimaryButton")
        # Override color specifically if needed, else rely on PrimaryButton
        btn_merge.clicked.connect(self.merge_pdfs)
        action_layout.addWidget(btn_merge)
        layout.addLayout(action_layout)

    def add_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDFs", "", "PDF Files (*.pdf)")
        if files:
            self.merge_files.extend(files)
            self.update_list()

    def update_list(self):
        self.pdf_list.clear()
        for f in self.merge_files:
            self.pdf_list.addItem(os.path.basename(f))

    def clear_pdfs(self):
        self.merge_files = []
        self.update_list()

    def merge_pdfs(self):
        if len(self.merge_files) < 2:
            QMessageBox.warning(self, "Warning", "Select at least 2 PDFs.")
            return
            
        out_path, _ = QFileDialog.getSaveFileName(self, "Save Merged PDF", "", "PDF Files (*.pdf)")
        if out_path:
            success, msg = PDFProcessor.merge_pdfs(self.merge_files, out_path)
            if success:
                QMessageBox.information(self, "Success", msg)
            else:
                QMessageBox.critical(self, "Error", msg)

    # ================= SPLIT TAB =================
    def init_split_tab(self):
        layout = QVBoxLayout(self.split_tab)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # File Selection
        file_box = QHBoxLayout()
        self.lbl_split_file = QLabel("No file selected")
        self.lbl_split_file.setStyleSheet("color: #909090; font-style: italic;")
        file_box.addWidget(self.lbl_split_file)
        
        btn_select = QPushButton("Select PDF")
        btn_select.setProperty("class", "SecondaryButton")
        btn_select.clicked.connect(self.select_split_file)
        file_box.addWidget(btn_select)
        layout.addLayout(file_box)
        
        layout.addSpacing(20)
        
        # Options Frame
        opts_frame = QFrame()
        opts_frame.setProperty("class", "ActionCard") # Reusing card style for container
        opts_layout = QVBoxLayout(opts_frame)
        
        layout.addWidget(opts_frame)
        
        self.rb_all = QRadioButton("Extract All Pages (Separate Files)")
        self.rb_all.setChecked(True)
        opts_layout.addWidget(self.rb_all)
        
        self.rb_range = QRadioButton("Extract Range (e.g. 1-5)")
        opts_layout.addWidget(self.rb_range)
        
        self.txt_range = QLineEdit()
        self.txt_range.setPlaceholderText("Enter range (e.g., 1-5 or 5)")
        opts_layout.addWidget(self.txt_range)
        
        layout.addStretch()
        
        # Action
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        btn_split = QPushButton("Process Split")
        btn_split.setProperty("class", "PrimaryButton")
        btn_split.clicked.connect(self.process_split)
        action_layout.addWidget(btn_split)
        layout.addLayout(action_layout)

    def select_split_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select PDF to Split", "", "PDF Files (*.pdf)")
        if f:
            self.split_file = f
            self.lbl_split_file.setText(os.path.basename(f))
            self.lbl_split_file.setStyleSheet("color: white; font-weight: bold;")

    def process_split(self):
        if not self.split_file:
            QMessageBox.warning(self, "Warning", "Please select a PDF file first.")
            return

        mode = "all" if self.rb_all.isChecked() else "range"
        page_range = self.txt_range.text().strip()
        
        if mode == "range" and not page_range:
             QMessageBox.warning(self, "Warning", "Please enter a page range.")
             return

        # Output Dir
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if output_dir:
            success, msg = PDFProcessor.split_pdf(self.split_file, output_dir, mode, page_range)
            if success:
                QMessageBox.information(self, "Success", msg)
            else:
                QMessageBox.critical(self, "Error", msg)

    # ================= COMPRESS TAB =================
    def init_compress_tab(self):
        layout = QVBoxLayout(self.compress_tab)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # File Selection
        file_box = QHBoxLayout()
        self.lbl_compress_file = QLabel("No file selected")
        self.lbl_compress_file.setStyleSheet("color: #909090; font-style: italic;")
        file_box.addWidget(self.lbl_compress_file)
        
        btn_select = QPushButton("Select PDF")
        btn_select.setProperty("class", "SecondaryButton")
        btn_select.clicked.connect(self.select_compress_file)
        file_box.addWidget(btn_select)
        layout.addLayout(file_box)
        
        layout.addSpacing(20)
        
        # Quality Selection
        quality_frame = QFrame()
        quality_frame.setProperty("class", "ActionCard")
        quality_layout = QVBoxLayout(quality_frame)
        
        QLabel_quality = QLabel("Compression Quality:")
        QLabel_quality.setStyleSheet("font-weight: bold; color: white;")
        quality_layout.addWidget(QLabel_quality)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Low (Smallest file)", "Medium (Balanced)", "High (Best quality)"])
        self.quality_combo.setCurrentIndex(1)
        quality_layout.addWidget(self.quality_combo)
        
        layout.addWidget(quality_frame)
        layout.addStretch()
        
        # Action
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        btn_compress = QPushButton("Compress PDF")
        btn_compress.setProperty("class", "PrimaryButton")
        btn_compress.clicked.connect(self.compress_pdf)
        action_layout.addWidget(btn_compress)
        layout.addLayout(action_layout)
    
    def select_compress_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select PDF to Compress", "", "PDF Files (*.pdf)")
        if f:
            self.compress_file = f
            # Show file info
            info = PDFProcessor.get_pdf_info(f)
            self.lbl_compress_file.setText(f"{os.path.basename(f)} ({info.get('size_mb', 0)} MB)")
            self.lbl_compress_file.setStyleSheet("color: white; font-weight: bold;")
    
    def compress_pdf(self):
        if not hasattr(self, 'compress_file') or not self.compress_file:
            QMessageBox.warning(self, "Warning", "Please select a PDF file first.")
            return
        
        quality_map = {0: "low", 1: "medium", 2: "high"}
        quality = quality_map[self.quality_combo.currentIndex()]
        
        out_path, _ = QFileDialog.getSaveFileName(self, "Save Compressed PDF", "", "PDF Files (*.pdf)")
        if out_path:
            success, msg = PDFProcessor.compress_pdf(self.compress_file, out_path, quality)
            if success:
                QMessageBox.information(self, "Success", msg)
            else:
                QMessageBox.critical(self, "Error", msg)



