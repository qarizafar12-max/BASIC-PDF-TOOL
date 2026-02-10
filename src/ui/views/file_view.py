import os
import shutil
import hashlib
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                                 QListWidget, QListWidgetItem, QFileDialog, QMessageBox, 
                                 QTabWidget, QLineEdit, QRadioButton, QFrame, QProgressBar,
                                 QTableWidget, QTableWidgetItem, QHeaderView, QComboBox)
from PySide6.QtCore import Qt, QThread, Signal

class DuplicateScanner(QThread):
    progress = Signal(int)
    finished = Signal(dict)
    
    def __init__(self, directory):
        super().__init__()
        self.directory = directory
        
    def run(self):
        duplicates = {}
        hashes = {}
        files_list = []
        
        for root, _, files in os.walk(self.directory):
            for f in files:
                files_list.append(os.path.join(root, f))
                
        total_files = len(files_list)
        
        for i, filepath in enumerate(files_list):
            try:
                with open(filepath, "rb") as f:
                    file_hash = hashlib.md5(f.read(4096)).hexdigest()
                    
                if file_hash in hashes:
                    if file_hash not in duplicates:
                        duplicates[file_hash] = [hashes[file_hash]]
                    duplicates[file_hash].append(filepath)
                else:
                    hashes[file_hash] = filepath
                    
                self.progress.emit(int((i / total_files) * 100))
            except:
                pass
                
        self.finished.emit(duplicates)

class FileView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabs
        self.tabs = QTabWidget()
        
        self.init_renamer_tab()
        self.init_organizer_tab()
        self.init_zip_tab()
        self.init_duplicates_tab()
        
        layout.addWidget(self.tabs)

    def init_renamer_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(40, 40, 40, 40)
        
        self.rename_files = []
        
        # List
        self.rename_list = QListWidget()
        # Stylesheet handles QListWidget
        layout.addWidget(self.rename_list)
        
        # Controls
        ctrl_layout = QHBoxLayout()
        btn_add = QPushButton("Add Files")
        btn_add.setProperty("class", "SecondaryButton")
        btn_add.clicked.connect(self.add_rename_files)
        ctrl_layout.addWidget(btn_add)
        
        btn_clear = QPushButton("Clear")
        btn_clear.setProperty("class", "DangerButton")
        btn_clear.clicked.connect(self.clear_rename_files)
        ctrl_layout.addWidget(btn_clear)
        layout.addLayout(ctrl_layout)
        
        layout.addSpacing(20)
        
        # Pattern
        form = QHBoxLayout()
        form.addWidget(QLabel("Pattern:"))
        self.txt_pattern = QLineEdit()
        self.txt_pattern.setPlaceholderText("File_### (### -> 001)")
        # Stylesheet handles QLineEdit
        form.addWidget(self.txt_pattern)
        
        btn_rename = QPushButton("Batch Rename")
        btn_rename.setProperty("class", "PrimaryButton")
        btn_rename.clicked.connect(self.process_rename)
        form.addWidget(btn_rename)
        layout.addLayout(form)
        
        self.tabs.addTab(tab, "Renamer")

    def add_rename_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        if files:
            self.rename_files.extend(files)
            self.update_rename_list()
            
    def update_rename_list(self):
        self.rename_list.clear()
        for f in self.rename_files:
            self.rename_list.addItem(os.path.basename(f))
            
    def clear_rename_files(self):
        self.rename_files = []
        self.update_rename_list()
        
    def process_rename(self):
        pattern = self.txt_pattern.text()
        if not pattern or not self.rename_files:
            QMessageBox.warning(self, "Error", "Pattern and files required.")
            return
            
        count = 1
        for old_path in self.rename_files:
            dir_name = os.path.dirname(old_path)
            ext = os.path.splitext(old_path)[1]
            
            # Simple pattern replacement
            new_name = pattern.replace("###", f"{count:03d}").replace("##", f"{count:02d}").replace("#", f"{count}") + ext
            new_path = os.path.join(dir_name, new_name)
            
            try:
                os.rename(old_path, new_path)
                count += 1
            except Exception as e:
                print(f"Error renaming {old_path}: {e}")
                
        QMessageBox.information(self, "Success", f"Renamed {count-1} files.")
        self.clear_rename_files()

    def init_organizer_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(40, 40, 40, 40)
        
        layout.addWidget(QLabel("Select Directory to Organize:"))
        
        hbox = QHBoxLayout()
        self.txt_org_dir = QLineEdit()
        self.txt_org_dir.setReadOnly(True)
        hbox.addWidget(self.txt_org_dir)
        
        btn_browse = QPushButton("Browse")
        btn_browse.setProperty("class", "SecondaryButton")
        btn_browse.clicked.connect(lambda: self.txt_org_dir.setText(QFileDialog.getExistingDirectory(self, "Select Directory")))
        hbox.addWidget(btn_browse)
        layout.addLayout(hbox)
        
        layout.addSpacing(20)
        
        layout.addWidget(QLabel("Organize By:"))
        self.combo_org_type = QComboBox()
        self.combo_org_type.addItems(["File Extension", "Date Created (Year/Month)"])
        layout.addWidget(self.combo_org_type)
        
        layout.addStretch()
        
        btn_org = QPushButton("Organize Files")
        btn_org.setProperty("class", "PrimaryButton")
        btn_org.clicked.connect(self.process_organize)
        layout.addWidget(btn_org)
        
        self.tabs.addTab(tab, "Organizer")
        
    def process_organize(self):
        directory = self.txt_org_dir.text()
        if not directory or not os.path.exists(directory):
            QMessageBox.warning(self, "Error", "Invalid directory.")
            return
            
        by_date = self.combo_org_type.currentIndex() == 1
        moved_count = 0
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isdir(filepath): continue
            
            try:
                if by_date:
                    ts = os.path.getmtime(filepath)
                    dt = datetime.fromtimestamp(ts)
                    folder_name = dt.strftime("%Y-%m")
                else:
                    ext = os.path.splitext(filename)[1].lower().replace('.', '')
                    folder_name = ext if ext else "no_extension"
                
                target_dir = os.path.join(directory, folder_name)
                os.makedirs(target_dir, exist_ok=True)
                
                shutil.move(filepath, os.path.join(target_dir, filename))
                moved_count += 1
            except Exception as e:
                print(f"Error moving {filename}: {e}")
                
        QMessageBox.information(self, "Success", f"Organized {moved_count} files.")

    def init_zip_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Tabs for Zip / Unzip inside
        sub_tabs = QTabWidget()
        layout.addWidget(sub_tabs)
        
        # Create Zip
        zip_widget = QWidget()
        z_layout = QVBoxLayout(zip_widget)
        z_layout.addWidget(QLabel("Files to Zip:"))
        
        self.zip_list = QListWidget()
        z_layout.addWidget(self.zip_list)
        
        z_btns = QHBoxLayout()
        btn_add_z = QPushButton("Add Files")
        btn_add_z.setProperty("class", "SecondaryButton")
        btn_add_z.clicked.connect(self.add_zip_files)
        z_btns.addWidget(btn_add_z)
        
        btn_create_z = QPushButton("Create Zip")
        btn_create_z.setProperty("class", "PrimaryButton")
        btn_create_z.clicked.connect(self.create_zip)
        z_btns.addWidget(btn_create_z)
        z_layout.addLayout(z_btns)
        
        sub_tabs.addTab(zip_widget, "Create Archive")
        
        # Extract Zip
        unzip_widget = QWidget()
        u_layout = QVBoxLayout(unzip_widget)
        
        u_layout.addWidget(QLabel("Select Archive:"))
        h_u = QHBoxLayout()
        self.txt_unzip_file = QLineEdit()
        h_u.addWidget(self.txt_unzip_file)
        btn_br_u = QPushButton("Browse")
        btn_br_u.setProperty("class", "SecondaryButton")
        btn_br_u.clicked.connect(lambda: self.txt_unzip_file.setText(QFileDialog.getOpenFileName(self, "Select Zip", "", "Zip Files (*.zip)")[0]))
        h_u.addWidget(btn_br_u)
        u_layout.addLayout(h_u)
        
        btn_extract = QPushButton("Extract Here")
        btn_extract.setProperty("class", "PrimaryButton")
        btn_extract.clicked.connect(self.extract_zip)
        u_layout.addWidget(btn_extract)
        u_layout.addStretch()
        
        sub_tabs.addTab(unzip_widget, "Extract Archive")
        
        self.tabs.addTab(tab, "Zip / Unzip")
        self.zip_files = []

    def add_zip_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        if files:
            self.zip_files.extend(files)
            for f in files:
                self.zip_list.addItem(os.path.basename(f))

    def create_zip(self):
        if not self.zip_files: return
        out, _ = QFileDialog.getSaveFileName(self, "Save Zip", "", "Zip Files (*.zip)")
        if out:
            import zipfile
            with zipfile.ZipFile(out, 'w') as zf:
                for f in self.zip_files:
                    zf.write(f, os.path.basename(f))
            QMessageBox.information(self, "Success", "Archive created.")
            self.zip_files = []
            self.zip_list.clear()

    def extract_zip(self):
        zip_path = self.txt_unzip_file.text()
        if not zip_path or not os.path.exists(zip_path): return
        
        out_dir = QFileDialog.getExistingDirectory(self, "Extract To")
        if out_dir:
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(out_dir)
            QMessageBox.information(self, "Success", "Extracted successfully.")

    def init_duplicates_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(40, 40, 40, 40)
        
        h_d = QHBoxLayout()
        self.txt_dup_dir = QLineEdit()
        self.txt_dup_dir.setPlaceholderText("Select directory to scan...")
        h_d.addWidget(self.txt_dup_dir)
        
        btn_scan = QPushButton("Scan for Duplicates")
        btn_scan.setProperty("class", "PrimaryButton")
        btn_scan.clicked.connect(self.scan_duplicates)
        h_d.addWidget(btn_scan)
        
        btn_br_d = QPushButton("Browse")
        btn_br_d.setProperty("class", "SecondaryButton")
        btn_br_d.clicked.connect(lambda: self.txt_dup_dir.setText(QFileDialog.getExistingDirectory(self, "Select Directory")))
        h_d.addWidget(btn_br_d)
        layout.addLayout(h_d)
        
        self.dup_progress = QProgressBar()
        self.dup_progress.setVisible(False)
        layout.addWidget(self.dup_progress)
        
        self.dup_list = QListWidget()
        layout.addWidget(self.dup_list)
        
        btn_del = QPushButton("Delete Selected Duplicates")
        btn_del.setProperty("class", "DangerButton")
        btn_del.clicked.connect(self.delete_duplicates)
        layout.addWidget(btn_del)
        
        self.tabs.addTab(tab, "Duplicate Remover")
        self.found_duplicates = {}

    def scan_duplicates(self):
        d = self.txt_dup_dir.text()
        if not d or not os.path.exists(d): return
        
        self.dup_list.clear()
        self.dup_progress.setVisible(True)
        self.dup_progress.setValue(0)
        
        self.scanner = DuplicateScanner(d)
        self.scanner.progress.connect(self.dup_progress.setValue)
        self.scanner.finished.connect(self.on_scan_finished)
        self.scanner.start()
        
    def on_scan_finished(self, duplicates):
        self.dup_progress.setVisible(False)
        self.found_duplicates = duplicates
        
        if not duplicates:
            QMessageBox.information(self, "Result", "No duplicates found.")
            return
            
        for h, paths in duplicates.items():
            # Add all but first one to list (keep one original)
            for p in paths[1:]:
                item = QListWidgetItem(p)
                item.setCheckState(Qt.Checked)
                self.dup_list.addItem(item)
                
        QMessageBox.information(self, "Result", f"Found {len(duplicates)} groups of duplicates.")

    def delete_duplicates(self):
        count = 0
        for i in range(self.dup_list.count()):
            item = self.dup_list.item(i)
            if item.checkState() == Qt.Checked:
                try:
                    os.remove(item.text())
                    count += 1
                except:
                    pass
        
        QMessageBox.information(self, "Success", f"Deleted {count} duplicate files.")
        self.dup_list.clear()
