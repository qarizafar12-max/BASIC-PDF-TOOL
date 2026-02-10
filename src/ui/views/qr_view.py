from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFileDialog, QMessageBox, QFrame, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage, QPainter, QColor
import qrcode
from PIL import Image
import io

class QRView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        header = QLabel("QR Code Generator")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Input Area
        input_frame = QFrame()
        input_frame.setStyleSheet("background: #1A1A1A; border-radius: 8px; padding: 20px;")
        input_layout = QVBoxLayout(input_frame)
        
        input_layout.addWidget(QLabel("Enter Text or URL:"))
        self.txt_input = QLineEdit()
        self.txt_input.setPlaceholderText("https://example.com")
        self.txt_input.setStyleSheet("background: #111; color: white; padding: 12px; border: 1px solid #333; border-radius: 6px; font-size: 14px;")
        self.txt_input.textChanged.connect(self.generate_qr)
        input_layout.addWidget(self.txt_input)
        
        layout.addWidget(input_frame)
        layout.addSpacing(20)
        
        # QR Display Area
        self.qr_frame = QFrame()
        self.qr_frame.setStyleSheet("background: white; border-radius: 12px;")
        self.qr_frame.setFixedSize(300, 300)
        
        # Center the QR frame
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(self.qr_frame)
        center_layout.addStretch()
        layout.addLayout(center_layout)
        
        # QR Label inside frame
        qr_layout = QVBoxLayout(self.qr_frame)
        self.lbl_qr = QLabel()
        self.lbl_qr.setAlignment(Qt.AlignCenter)
        qr_layout.addWidget(self.lbl_qr)
        
        layout.addSpacing(30)
        
        # Actions
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        
        btn_save = QPushButton("Save QR Code")
        btn_save.setProperty("class", "PrimaryButton")
        btn_save.setMinimumWidth(150)
        btn_save.clicked.connect(self.save_qr)
        action_layout.addWidget(btn_save)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        layout.addStretch()
        
        # Initial empty state
        self.current_img = None
        self.generate_qr()

    def generate_qr(self):
        text = self.txt_input.text().strip()
        if not text:
            self.lbl_qr.setText("Enter text to generate")
            self.lbl_qr.setStyleSheet("color: black; font-size: 14px;")
            self.current_img = None
            return
            
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            self.current_img = img
            
            # Convert to QPixmap
            im_data = img.convert("RGBA").tobytes("raw", "RGBA")
            qim = QImage(im_data, img.size[0], img.size[1], QImage.Format_RGBA8888)
            pix = QPixmap.fromImage(qim)
            
            # Scale to fit
            self.lbl_qr.setPixmap(pix.scaled(260, 260, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
        except Exception as e:
            self.lbl_qr.setText(f"Error: {e}")

    def save_qr(self):
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "Please generate a QR code first.")
            return
            
        path, _ = QFileDialog.getSaveFileName(self, "Save QR Code", "", "PNG Images (*.png);;All Files (*)")
        if path:
            try:
                self.current_img.save(path)
                QMessageBox.information(self, "Success", f"QR Code saved to {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {e}")
