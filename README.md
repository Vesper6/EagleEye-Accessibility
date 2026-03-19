# 🦅 EagleEye (鹰眼)

![Python Version](https://img.shields.io/badge/python-3.13-blue)
![Platform](https://img.shields.io/badge/platform-windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)
![Release](https://img.shields.io/github/v/release/Vesper6/EagleEye-Accessibility)

**EagleEye** 是一款专为 Windows 开发者和自动化爱好者设计的轻量级窗口句柄嗅探工具。它解决了老牌工具在高分屏（DPI 缩放）下的定位偏差痛点，提供优雅的实时交互反馈。

### 🌟 核心亮点
- **🎯 零误差定位**：完美适配 125%、150%、200% 等高 DPI 缩放，准星指哪打哪。
- **🌈 视觉反馈**：
  - **动态红框**：实时追踪并框选目标窗口。
  - **点击涟漪**：左键翡翠绿、右键太阳黄动态特效，让调试动作清晰可见。
- **🚀 极速运行**：基于 Python 3.13 与 PyQt6，采用 Nuitka 深度编译，单文件免安装运行。
- **隐藏运行**：支持最小化至系统托盘，`Ctrl + Alt + S` 快捷键瞬间唤醒。

### 🛠️ 技术栈
- **核心**: Python 3.13, Win32API
- **界面**: PyQt6 (High DPI Support)
- **监听**: pynput, keyboard
- **构建**: Nuitka (Onefile Mode)
  
### 🚀 快速开始
1. 克隆仓库: `git clone https://github.com/Vesper6/EagleEye-Accessibility.git`
2. 安装依赖: `pip install -r requirements.txt`
3. 运行: `python main.py`

### 📥 立即下载
请前往 [Releases 页面](https://github.com/Vesper6/EagleEye-Accessibility/releases) 下载最新的 `EagleEye.exe`。

> **注意**：由于未经过数字签名，运行时如遇 Windows SmartScreen 拦截，请点击“更多信息” -> “仍要运行”。

---
**Developed by Vesper6 @ SkillGo Team**
