import sys
import os
import keyboard
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout,
                             QWidget, QLabel, QSystemTrayIcon, QMenu, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QLockFile, QDir
from PyQt6.QtGui import QIcon, QAction
from pynput import mouse
from core.overlay import FocusOverlay


def resource_path(relative_path):
    """ 专门为 Nuitka/PyInstaller 单文件模式优化的路径获取函数 """
    # 1. 检查是否在单文件运行环境 (Nuitka/PyInstaller 都会模拟这个路径)
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

    # 2. 拼接绝对路径
    path = os.path.join(base_path, relative_path)

    # 3. 调试日志 (编译后如果还有问题，可以去掉 --windows-disable-console 查看输出)
    # print(f"尝试加载资源: {path} | 存在: {os.path.exists(path)}")

    return path

class Bridge(QObject):
    """信号桥接类：处理跨线程的快捷键和鼠标点击"""
    hotkey_pressed = pyqtSignal()
    mouse_clicked = pyqtSignal(float, float, bool)


class ControlWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 1. 初始化图标 (托盘显示的核心)
        self.icon_path = resource_path("logo.ico")
        if os.path.exists(self.icon_path):
            self.app_icon = QIcon(self.icon_path)
        else:
            print(f"警告: 找不到图标文件 {self.icon_path}，将使用系统默认")
            self.app_icon = QIcon()

        self.setWindowIcon(self.app_icon)
        self.setWindowTitle("EagleEye 控制中心")
        self.setFixedSize(320, 420)

        # 2. 状态与逻辑初始化
        self.is_running = False
        # 初始化时 Overlay 是隐藏的
        self.overlay = FocusOverlay(self.app_icon)
        self.bridge = Bridge()

        # 3. 信号绑定
        keyboard.add_hotkey('ctrl+alt+s', lambda: self.bridge.hotkey_pressed.emit())
        self.bridge.hotkey_pressed.connect(self.toggle_eye)
        self.bridge.mouse_clicked.connect(self.overlay.trigger_click_effect)
        self.overlay.info_updated.connect(self.update_display)

        # 4. UI与托盘
        self.init_ui()
        self.create_tray()

        # 5. 全局鼠标监听 (用于点击特效)
        self.mouse_listener = mouse.Listener(on_click=self.on_global_click)
        self.mouse_listener.start()

    def on_global_click(self, x, y, button, pressed):
        """鼠标监听回调：将坐标发送给 Overlay"""
        if pressed and self.is_running and button != mouse.Button.middle:
            is_left = (button == mouse.Button.left)
            scale = self.overlay.screen().devicePixelRatio()
            # 发射逻辑坐标
            self.bridge.mouse_clicked.emit(x / scale, y / scale, is_left)

    def init_ui(self):
        """初始化主界面布局"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # 状态标题
        self.status_label = QLabel("当前状态：已停止")
        self.status_label.setStyleSheet("font-weight: bold; color: #666; font-size: 14px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.status_label)

        # 数据面板
        self.info_group = QWidget()
        self.info_group.setStyleSheet(
            "background-color: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; padding: 10px;")
        info_layout = QVBoxLayout(self.info_group)

        self.lbl_title = QLabel("窗口标题: -")
        self.lbl_id = QLabel("句柄 ID: -")
        self.lbl_class = QLabel("窗口类名: -")

        # 坐标显示行
        coords_widget = QWidget()
        coords_layout = QHBoxLayout(coords_widget)
        coords_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_pos_x = QLabel("鼠标 X: -")
        self.lbl_pos_y = QLabel("鼠标 Y: -")
        coords_layout.addWidget(self.lbl_pos_x)
        coords_layout.addWidget(self.lbl_pos_y)

        font_style = "font-family: 'Consolas', '微软雅黑'; font-size: 11px;"
        for lbl in [self.lbl_title, self.lbl_id, self.lbl_class, self.lbl_pos_x, self.lbl_pos_y]:
            lbl.setStyleSheet(font_style)
            lbl.setWordWrap(True)
            if lbl not in [self.lbl_pos_x, self.lbl_pos_y]:
                info_layout.addWidget(lbl)

        info_layout.addWidget(coords_widget)
        self.layout.addWidget(self.info_group)

        # 开启/关闭按钮
        self.btn_toggle = QPushButton("开启鹰眼 (Ctrl+Alt+S)")
        self.btn_toggle.setFixedHeight(60)
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.toggle_eye)
        self.layout.addWidget(self.btn_toggle)

    def toggle_eye(self):
        """切换鹰眼模式的状态"""
        self.is_running = not self.is_running
        if self.is_running:
            self.overlay.showFullScreen()
            self.status_label.setText("当前状态：🚀 运行中")
            self.status_label.setStyleSheet("font-weight: bold; color: #2ecc71; font-size: 14px;")
            self.btn_toggle.setText("关闭鹰眼")
            self.btn_toggle.setStyleSheet(
                "background-color: #e74c3c; color: white; font-weight: bold; border-radius: 5px;")
        else:
            self.overlay.hide()
            self.status_label.setText("当前状态：已停止")
            self.status_label.setStyleSheet("font-weight: bold; color: #666; font-size: 14px;")
            self.btn_toggle.setText("开启鹰眼")
            self.btn_toggle.setStyleSheet("")

    def update_display(self, title, hwnd_id, class_name, mx, my):
        """刷新界面上的文本信息"""
        self.lbl_pos_x.setText(f"鼠标 X: {mx}")
        self.lbl_pos_y.setText(f"鼠标 Y: {my}")
        clean_title = title.strip() or "无标题窗口"
        display_title = (clean_title[:25] + '...') if len(clean_title) > 25 else clean_title
        self.lbl_title.setText(f"窗口标题: {display_title}")
        self.lbl_id.setText(f"句柄 ID: {hwnd_id}")
        self.lbl_class.setText(f"窗口类名: {class_name}")

    def create_tray(self):
        """创建系统托盘，防止主界面关闭后程序直接退出"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.app_icon)
        self.tray_icon.setToolTip("EagleEye 鹰眼控制中心")

        tray_menu = QMenu()
        show_action = QAction("显示主面板", self)
        show_action.triggered.connect(self.show_normal_and_raise)

        quit_action = QAction("彻底退出", self)
        quit_action.triggered.connect(self.safe_quit)

        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        # 双击托盘图标恢复窗口
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def show_normal_and_raise(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_normal_and_raise()

    def safe_quit(self):
        """安全退出，释放全局热键"""
        keyboard.unhook_all()
        QApplication.instance().quit()

    def closeEvent(self, event):
        """重写关闭事件，使其点击关闭按钮时隐藏到托盘"""
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                "EagleEye",
                "程序已隐藏至后台运行",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
            event.ignore()





if __name__ == "__main__":
    # 启用高DPI适配
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # --- 核心：禁止多开逻辑 ---
    lock_path = QDir.tempPath() + "/eagleeye_v1_0_3.lock"
    lock_file = QLockFile(lock_path)
    if not lock_file.tryLock(100):
        QMessageBox.warning(None, "EagleEye", "程序已在运行中，请检查系统托盘。")
        sys.exit(0)

    window = ControlWindow()
    window.show()

    # 将 lock_file 保存在内存中直到程序结束
    sys.exit(app.exec())