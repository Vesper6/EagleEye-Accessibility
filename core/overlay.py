import sys
import win32gui
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt, QTimer, QRect, QPoint, pyqtSignal, QVariantAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QPen, QColor, QCursor


class FocusOverlay(QMainWindow):
    info_updated = pyqtSignal(str, str, str, int, int)

    def __init__(self, icon):
        super().__init__()
        self.setWindowIcon(icon)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 【修改】初始化时不调用 showFullScreen()，保持隐藏

        self.mouse_pos = QPoint(0, 0)
        self.target_rect = QRect(0, 0, 0, 0)
        self.anim_value = 0
        self.line_color = QColor(255, 0, 0, 100)
        self.anim_pos = QPoint(0, 0)
        self.is_left_click = True

        self.click_anim = QVariantAnimation(self)
        self.click_anim.setDuration(400)
        self.click_anim.setStartValue(0)
        self.click_anim.setEndValue(100)
        self.click_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.click_anim.valueChanged.connect(self._on_anim_step)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(16)

    def _on_anim_step(self, value):
        self.anim_value = value
        self.update()

    def trigger_click_effect(self, logical_x, logical_y, is_left=True):
        self.anim_pos = QPoint(int(logical_x), int(logical_y))
        self.is_left_click = is_left
        self.line_color = QColor(46, 204, 113, 220) if is_left else QColor(241, 196, 15, 220)
        self.click_anim.stop()
        self.click_anim.start()
        self.update()
        QTimer.singleShot(500, self._reset_line_color)

    def _reset_line_color(self):
        self.line_color = QColor(255, 0, 0, 100)
        self.update()

    def refresh(self):
        if not self.isVisible(): return  # 隐藏时不消耗资源计算坐标

        self.mouse_pos = QCursor.pos()
        scale = self.screen().devicePixelRatio()
        px, py = int(self.mouse_pos.x() * scale), int(self.mouse_pos.y() * scale)
        hwnd = win32gui.WindowFromPoint((px, py))
        mx, my = self.mouse_pos.x(), self.mouse_pos.y()

        if hwnd:
            title = win32gui.GetWindowText(hwnd) or "无标题窗口"
            cid = hex(hwnd)
            cname = win32gui.GetClassName(hwnd)
            self.info_updated.emit(title, cid, cname, mx, my)
            rect = win32gui.GetWindowRect(hwnd)
            l, t, r, b = rect
            self.target_rect = QRect(int(l / scale), int(t / scale), int((r - l) / scale), int((b - t) / scale))
        else:
            self.info_updated.emit("-", "-", "-", mx, my)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(self.line_color, 1, Qt.PenStyle.DashLine))
        painter.drawLine(0, self.mouse_pos.y(), self.width(), self.mouse_pos.y())
        painter.drawLine(self.mouse_pos.x(), 0, self.mouse_pos.x(), self.height())

        if self.click_anim.state() == QVariantAnimation.State.Running:
            alpha = int(255 * (1 - self.anim_value / 100))
            color = QColor(self.line_color.red(), self.line_color.green(), self.line_color.blue(), alpha)
            painter.setPen(QPen(color, 2))
            if self.is_left_click:
                radius = int(self.anim_value * 0.8)
                painter.drawEllipse(self.anim_pos, radius, radius)
            else:
                size = int(100 - self.anim_value)
                painter.drawRect(self.anim_pos.x() - size // 2, self.anim_pos.y() - size // 2, size, size)

        if not self.target_rect.isNull():
            painter.setPen(QPen(QColor(255, 0, 0, 180), 2))
            painter.drawRect(self.target_rect)