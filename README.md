# 🦅 EagleEye (鹰眼) - 窗口句柄嗅探工具

**EagleEye** 是一款基于 Python 3.13 和 PyQt6 开发的轻量级 Windows 辅助工具。它可以实时追踪鼠标下的窗口句柄信息，并提供直观的视觉反馈。

### ✨ 核心特性
- **DPI 智能适配**：完美支持 4K 屏幕及高缩放比例，坐标定位零误差。
- **实时数据提取**：自动获取窗口标题、HWND 句柄 ID、类名及鼠标逻辑坐标。
- **交互动效**：全局监听点击事件，提供绿色（左键）与黄色（右键）动态反馈。
- **静默运行**：支持最小化至系统托盘，通过 `Ctrl + Alt + S` 快速唤醒。
- **单实例运行**：内置文件锁，防止程序多开导致资源占用。

### 🛠️ 开发环境
- **Language**: Python 3.13
- **Framework**: PyQt6
- **Build Tool**: Nuitka (Standalone & Onefile)

### 🚀 快速开始
1. 克隆仓库: `git clone https://github.com/Vesper6/EagleEye-Accessibility.git`
2. 安装依赖: `pip install -r requirements.txt`
3. 运行: `python main.py`