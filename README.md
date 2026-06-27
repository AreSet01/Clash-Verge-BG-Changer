# Clash Verge Rev 背景替换与极简水晶毛玻璃工具 (Clash Verge BG Changer)

一个专为 **Clash Verge Rev** 设计的桌面轻量工具，支持一键替换客户端自定义背景图片，并内置 macOS 级极简水晶毛玻璃卡片样式美化，全面提升客户端视觉质感。

---

## ✨ 核心特性

- 🖼️ **自定义背景壁纸**：支持上传 JPEG、PNG、WebP 等多种主流格式图片作为客户端底层壁纸。
- ⚡ **自动图片压缩与 Base64 转换**：自动将大图压缩至适宜分辨率与体积并转为 Base64 注入，避免占用过高系统内存。
- 🪟 **水晶毛玻璃卡片美化**：
  - 彻底清除全布局深色/白色底色背景，让底层壁纸完全显现。
  - 深度适配 **首页 (Home)**、**代理 (Proxies)**、**订阅 (Profiles)** 等核心页面卡片。
  - **Proxies 页面** 代理节点与代理组悬浮毛玻璃质感与选中态高亮。
  - **Profiles 页面** 订阅卡片外壳高透毛玻璃，完美保留原生选中态左边框。
- 🌓 **暗黑模式智能适配**：内置 `html.dark` 与 `prefers-color-scheme: dark` 规则，暗色模式下防眩光，玻璃对比度更舒适。
- 🖥️ **跨平台支持**：支持 macOS 及 Windows 系统环境的 Clash Verge Rev 配置文件路径自动识别。

---

## 🚀 使用方法

### 方法一：使用编译好的 macOS 应用（推荐）
1. 从 GitHub [Releases](https://github.com/AreSet01/Clash-Verge-BG-Changer/releases) 页面下载最新的 `ClashVerge_BG_Changer_macOS.zip`。
2. 解压并运行 `ClashVerge_BG_Changer.app`。
3. 在软件界面中点击 **“选择图片”** 并设置满意的不透明度（推荐 `0.7` - `0.9`）。
4. 点击 **“应用背景”**。
5. ⚠️ **重要步骤**：在系统状态栏/托盘图标彻底右键退出 Clash Verge Rev 客户端并重新打开，使新的 CSS 生效。

### 方法二：直接运行 Python 脚本
要求：安装有 `Python 3.x` 以及 `Pillow` 和 `PyYAML` 依赖库（脚本会在运行时自动检测并尝试安装缺失依赖）。

```bash
python3 ClashVergeBGChanger.pyw
```

---

## 🛠️ 自行打包构建 (PyInstaller)

如果你希望自行打包为独立应用程序：

```bash
pip install pyinstaller pillow pyyaml
pyinstaller --windowed --noconfirm --name=ClashVerge_BG_Changer ClashVergeBGChanger.pyw
```

---

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。欢迎 Pull Request 或提交 Issue 进行交流与反馈！
