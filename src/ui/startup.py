import sys
import math
import random
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect, QApplication
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Signal, QRectF, QPointF
from PySide6.QtGui import QFont, QColor, QPainter, QLinearGradient, QBrush, QPen, QRadialGradient

class Particle:
    def __init__(self, w, h):
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.speed = random.uniform(0.5, 2.0)
        self.radius = random.uniform(1.0, 3.0)
        self.angle = random.uniform(0, 2 * math.pi)
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed
        self.alpha = random.uniform(50, 200)

    def move(self, w, h):
        self.x += self.dx
        self.y += self.dy
        
        # Wrap around
        if self.x < 0: self.x = w
        if self.x > w: self.x = 0
        if self.y < 0: self.y = h
        if self.y > h: self.y = 0

class StartupScreen(QWidget):
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(700, 450)
        self.center()
        
        # Animation State
        self.hue_shift = 0.0
        self.particles = [Particle(self.width(), self.height()) for _ in range(50)]
        
        # Timer for 60FPS update
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16) # ~60 FPS
        
        # Internal Timer for sequence
        self.sequence_step = 0
        QTimer.singleShot(500, self.next_sequence) # Start fade in text
        QTimer.singleShot(4500, self.close_animation) # End

        # UI Setup (Text Overlay)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        
        self.lbl_logo = QLabel("EXCODE")
        self.lbl_logo.setAlignment(Qt.AlignCenter)
        self.lbl_logo.setStyleSheet("""
            color: white;
            font-family: 'Segoe UI', sans-serif;
            font-size: 80px;
            font-weight: 900;
            letter-spacing: 15px;
        """)
        
        # Shadow effect via GraphicsEffect is tricky with transparent bg painting, 
        # so we rely on the contrast of the bg.
        
        self.lbl_sub = QLabel("PREMIUM AI TOOLS AVAILABLE")
        self.lbl_sub.setAlignment(Qt.AlignCenter)
        self.lbl_sub.setStyleSheet("""
            color: rgba(255, 255, 255, 200);
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
            font-weight: 400;
            letter-spacing: 6px;
            margin-top: 10px;
            padding-bottom: 20px;
        """)
        
        layout.addWidget(self.lbl_logo)
        layout.addWidget(self.lbl_sub)
        
        # Opacity for fade in
        self.op_logo = QGraphicsOpacityEffect(self.lbl_logo)
        self.lbl_logo.setGraphicsEffect(self.op_logo)
        self.op_logo.setOpacity(0)
        
        self.op_sub = QGraphicsOpacityEffect(self.lbl_sub)
        self.lbl_sub.setGraphicsEffect(self.op_sub)
        self.op_sub.setOpacity(0)

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def update_animation(self):
        self.hue_shift += 0.5
        if self.hue_shift > 360:
            self.hue_shift = 0
            
        # Update particles
        for p in self.particles:
            p.move(self.width(), self.height())
            
        self.update() # Trigger paintEvent

    def next_sequence(self):
        # Animate Logo Fade In
        self.anim1 = QPropertyAnimation(self.op_logo, b"opacity")
        self.anim1.setDuration(1500)
        self.anim1.setStartValue(0)
        self.anim1.setEndValue(1)
        self.anim1.setEasingCurve(QEasingCurve.OutExpo)
        self.anim1.start()
        
        # Animate Sub Fade In slightly later
        QTimer.singleShot(800, self.animate_sub)

    def animate_sub(self):
        self.anim2 = QPropertyAnimation(self.op_sub, b"opacity")
        self.anim2.setDuration(1500)
        self.anim2.setStartValue(0)
        self.anim2.setEndValue(1)
        self.anim2.setEasingCurve(QEasingCurve.OutExpo)
        self.anim2.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 1. Background Gradient (Dynamic RGB)
        # We create a sweeping gradient based on hue_shift
        
        rect = self.rect()
        
        # Color 1
        c1 = QColor.fromHslF((self.hue_shift % 360) / 360.0, 0.8, 0.15)
        # Color 2 (offset hue)
        c2 = QColor.fromHslF(((self.hue_shift + 180) % 360) / 360.0, 0.8, 0.05)
        
        gradient = QLinearGradient(0, 0, rect.width(), rect.height())
        gradient.setColorAt(0, c1)
        gradient.setColorAt(1, c2)
        
        # Draw Rounded Rect Background
        path = QRectF(rect)
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(path, 30, 30)
        
        # 2. Border Gradient (Scanning/Glowing)
        border_pen = QPen()
        border_pen.setWidth(3)
        
        # rotating border gradient
        b_grad = QLinearGradient(0, 0, rect.width(), rect.height())
        # Shift colors faster for border
        bc1 = QColor.fromHslF(((self.hue_shift * 2) % 360) / 360.0, 1.0, 0.6)
        bc2 = QColor.fromHslF(((self.hue_shift * 2 + 180) % 360) / 360.0, 1.0, 0.6)
        b_grad.setColorAt(0, bc1)
        b_grad.setColorAt(1, bc2)
        
        border_pen.setBrush(QBrush(b_grad))
        painter.setPen(border_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(path.adjusted(1.5, 1.5, -1.5, -1.5), 30, 30)
        
        # 3. Particles
        painter.setPen(Qt.NoPen)
        for p in self.particles:
            # Particle color related to hue but lighter
            pc = QColor.fromHslF(((self.hue_shift + p.x) % 360) / 360.0, 0.8, 0.7)
            pc.setAlpha(int(p.alpha))
            painter.setBrush(pc)
            painter.drawEllipse(QPointF(p.x, p.y), p.radius, p.radius)

    def close_animation(self):
        self.timer.stop()
        self.anim_out = QPropertyAnimation(self, b"windowOpacity")
        self.anim_out.setDuration(500)
        self.anim_out.setStartValue(1)
        self.anim_out.setEndValue(0)
        self.anim_out.finished.connect(self.on_finished)
        self.anim_out.start()

    def on_finished(self):
        self.close()
        self.finished.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StartupScreen()
    window.show()
    sys.exit(app.exec())
