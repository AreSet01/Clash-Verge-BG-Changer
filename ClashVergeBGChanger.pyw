import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import base64
import traceback

LOG_FILE = os.path.expanduser("~/Desktop/ClashVergeChanger_Debug.log")

def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except:
        pass

log("--- App started ---")

def install_package(package):
    try:
        log(f"Installing {package}...")
        if os.name == 'nt':
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], creationflags=0x08000000)
        else:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        log(f"Installed {package} successfully.")
    except Exception as e:
        log(f"Failed to install {package}: {e}")
        messagebox.showerror("错误", f"自动安装依赖包 '{package}' 失败。请手动安装。\n{e}")
        sys.exit(1)

try:
    import yaml
except ImportError:
    install_package("pyyaml")
    import yaml

try:
    from PIL import Image, ImageTk
except ImportError:
    install_package("Pillow")
    from PIL import Image, ImageTk

def get_config_path():
    possible_dirs = []
    
    if os.name == 'nt':
        appdata = os.environ.get('APPDATA', '')
        possible_dirs = [
            os.path.join(appdata, 'io.github.clash-verge-rev.clash-verge-rev'),
            os.path.join(appdata, 'clash-verge-rev'),
            os.path.join(appdata, 'clash-verge')
        ]
    else:
        app_support = os.path.expanduser('~/Library/Application Support')
        possible_dirs = [
            os.path.join(app_support, 'io.github.clash-verge-rev.clash-verge-rev'),
            os.path.join(app_support, 'clash-verge-rev'),
            os.path.join(app_support, 'clash-verge')
        ]
        
    for d in possible_dirs:
        yaml_path = os.path.join(d, 'verge.yaml')
        if os.path.exists(yaml_path):
            log(f"Found config at {yaml_path}")
            return yaml_path
            
    log("Config not found")
    return None

CONFIG_PATH = get_config_path()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Clash Verge Rev 背景替换工具")
        self.root.resizable(True, True)
        self.root.minsize(450, 350)
        
        if not CONFIG_PATH:
            messagebox.showerror("错误", "未能找到 Clash Verge Rev 的配置文件 (verge.yaml)。\n请确认软件已安装并运行过至少一次。")
            sys.exit(1)
            
        self.config_data = self.load_config()
        self.selected_image_path = None
        self.opacity = tk.DoubleVar(value=0.8)
        self.preview_image = None
        
        self.setup_ui()
        
    def load_config(self):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            log(f"Load config error: {e}")
            messagebox.showerror("错误", f"读取配置文件失败:\n{e}")
            return {}

    def save_config(self):
        try:
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, allow_unicode=True, default_flow_style=False)
            log("Config saved successfully.")
            messagebox.showinfo("成功", "背景设置应用成功！\n\n请完全退出并重新打开 Clash Verge Rev，或在软件内重载配置以使更改生效。")
        except Exception as e:
            log(f"Save config error: {e}")
            messagebox.showerror("错误", f"保存配置文件失败:\n{e}")

    def setup_ui(self):
        tk.Label(self.root, text="请选择一张图片作为背景：", font=("Microsoft YaHei", 12)).pack(pady=5)
        
        # 增加一个醒目的红色提示，提醒用户必须先退出 Clash Verge Rev
        tk.Label(self.root, text="⚠️ 重要：点击应用前，请必须先完全退出 Clash Verge Rev！", fg="red", font=("Microsoft YaHei", 10, "bold")).pack(pady=2)
        
        self.lbl_path = tk.Label(self.root, text="未选择图片", fg="gray", wraplength=400)
        self.lbl_path.pack(pady=5)
        
        btn_select = tk.Button(self.root, text="选择图片", command=self.select_image, width=20)
        btn_select.pack(pady=5)
        
        self.lbl_preview = tk.Label(self.root, text="图片预览区", bg="#e0e0e0", width=40, height=10)
        self.lbl_preview.pack(pady=10, padx=20)
        
        tk.Label(self.root, text="背景不透明度 (推荐 0.7 - 0.9)：").pack(pady=(5, 0))
        self.slider_opacity = ttk.Scale(self.root, from_=0.1, to=1.0, orient='horizontal', variable=self.opacity, length=250)
        self.slider_opacity.pack(pady=5)
        
        frame_actions = tk.Frame(self.root)
        frame_actions.pack(pady=10)
        
        btn_apply = tk.Button(frame_actions, text="应用背景", command=self.apply_background, bg="#4CAF50", fg="black", width=12)
        btn_apply.grid(row=0, column=0, padx=15)
        
        btn_clear = tk.Button(frame_actions, text="清除背景", command=self.clear_background, bg="#f44336", fg="black", width=12)
        btn_clear.grid(row=0, column=1, padx=15)
        
        lbl_status = tk.Label(self.root, text=f"配置文件已加载: {os.path.basename(os.path.dirname(CONFIG_PATH))}", fg="green", font=("Microsoft YaHei", 8))
        lbl_status.pack(side="bottom", pady=5)
        
    def select_image(self):
        try:
            filetypes = [
                ('图片文件', '*.jpg *.jpeg *.png *.gif *.webp *.bmp'),
                ('所有文件', '*.*')
            ]
            filename = filedialog.askopenfilename(title='打开图片', initialdir=os.path.expanduser('~'), filetypes=filetypes)
            log(f"Selected file: {filename}")
            
            if filename:
                self.selected_image_path = filename
                self.lbl_path.config(text=filename, fg="black")
                self.show_preview(filename)
        except Exception as e:
            log(f"Error in select_image: {traceback.format_exc()}")
            messagebox.showerror("错误", f"选择图片时出错:\n{e}")

    def show_preview(self, image_path):
        try:
            log(f"Loading preview for: {image_path}")
            img = Image.open(image_path)
            orig_w, orig_h = img.size
            log(f"Original size: {orig_w}x{orig_h}")
            
            max_w = 500
            if orig_w > max_w:
                ratio = max_w / orig_w
                new_w = max_w
                new_h = int(orig_h * ratio)
            else:
                new_w = orig_w
                new_h = orig_h
                
            log(f"Resizing to: {new_w}x{new_h}")
            try:
                resample_filter = Image.Resampling.LANCZOS
            except AttributeError:
                resample_filter = Image.LANCZOS
                
            img = img.resize((new_w, new_h), resample_filter)
            self.preview_image = ImageTk.PhotoImage(img)
            
            # 重要修复：保留直接的引用，防止 Mac 下 Tkinter 的图片被垃圾回收或无法渲染
            self.lbl_preview.image = self.preview_image
            self.lbl_preview.config(image=self.preview_image, text="", width=new_w, height=new_h)
            
            required_height = new_h + 350
            current_w = max(450, new_w + 40)
            self.root.geometry(f"{current_w}x{required_height}")
            
            # 强制刷新界面，确保图片立刻画出来
            self.root.update_idletasks()
            log("Preview loaded successfully.")
            
        except Exception as e:
            log(f"Error in show_preview: {traceback.format_exc()}")
            messagebox.showerror("预览错误", f"无法加载图片预览：\n{e}")

    def generate_css(self, image_path, opacity):
        log("Generating CSS with compression...")
        import io
        
        try:
            # 1. 加载并压缩图片
            img = Image.open(image_path)
            
            # 如果图片不是RGB（比如带透明通道的PNG或RGBA），转为RGB以保存为JPEG
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            orig_w, orig_h = img.size
            max_bg_w = 1920
            max_bg_h = 1080
            
            # 按比例缩小到最大1920x1080，避免占用过大内存并缩小Base64体积
            if orig_w > max_bg_w or orig_h > max_bg_h:
                ratio = min(max_bg_w / orig_w, max_bg_h / orig_h)
                new_w = int(orig_w * ratio)
                new_h = int(orig_h * ratio)
                log(f"Compressing background image from {orig_w}x{orig_h} to {new_w}x{new_h}")
                try:
                    resample_filter = Image.Resampling.LANCZOS
                except AttributeError:
                    resample_filter = Image.LANCZOS
                img = img.resize((new_w, new_h), resample_filter)
            
            # 2. 将压缩后的图片保存到内存中的 BytesIO 对象
            buffer = io.BytesIO()
            # 统一保存为 JPEG 格式，质量 85，极大减小体积
            img.save(buffer, format="JPEG", quality=85)
            img_data = buffer.getvalue()
            
            # 3. 转换为 Base64
            encoded_string = base64.b64encode(img_data).decode('utf-8')
            data_uri = f"data:image/jpeg;base64,{encoded_string}"
            
            log(f"Image compressed and encoded. Base64 length: {len(encoded_string)}")
            
            css = f"""/* 设置背景图片到底层 (自动压缩+Base64直出) */
body::before {{
    content: "" !important;
    position: fixed !important;
    inset: 0 !important;
    background-image: url('{data_uri}') !important;
    background-size: cover !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    opacity: {opacity:.2f} !important;
    z-index: -1 !important;
    pointer-events: none !important;
}}

/* 强制彻底清除所有布局容器的深色底色，让背景完全透出 */
body, #root, #app, main, .layout, .layout-content, 
.base-page, .base-container, .base-container > section, .base-content,
.MuiContainer-root, .MuiGrid-root, .MuiGrid2-root,
div[class*="layout"], div[class*="container"], div[class*="content"], div[class*="page"] {{
    background-color: transparent !important;
    background: transparent !important;
}}

/* =========================================
   统一玻璃质感卡片核心逻辑 (Home, Proxies, Profiles)
   ========================================= */

/* 1. 基础卡片容器 (Home 页面大卡片, Profiles 页面卡片外壳) */
.MuiPaper-root, .MuiCard-root, .MuiDialog-paper, .MuiDrawer-paper, .MuiMenu-paper, 
.card, .panel, .wrapper,
.base-content div[class*="MuiGrid"] > .MuiBox-root,
.base-content div[class*="MuiGrid"] > div[class*="MuiGrid"] > .MuiBox-root,
.base-content > div > div[class*="MuiGrid"] > div[class*="MuiGrid"] > .MuiBox-root {{
    background-color: rgba(255, 255, 255, 0.1) !important;
    background-image: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.0) 100%) !important;
    backdrop-filter: blur(24px) saturate(150%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(150%) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.3) !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1) !important;
    border-radius: 12px !important;
    transition: all 0.3s ease;
}}

/* 2. 让 Profiles 页面的内层 ProfileBox 背景透明，透出外壳的玻璃质感，同时保留其原生的选中状态左边框 */
.base-content div[class*="MuiGrid"] > .MuiBox-root > .MuiBox-root[aria-selected],
.base-content div[class*="MuiGrid"] > div[class*="MuiGrid"] > .MuiBox-root > .MuiBox-root[aria-selected],
.base-content > div > div[class*="MuiGrid"] > div[class*="MuiGrid"] > .MuiBox-root > .MuiBox-root[aria-selected] {{
    background-color: transparent !important;
    background-image: none !important;
    box-shadow: none !important;
}}

/* 3. Proxies 页面：未选中的代理组和代理节点 */
.base-content .MuiListItemButton-root:not(.Mui-selected) {{
    background-color: rgba(255, 255, 255, 0.1) !important;
    background-image: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.0) 100%) !important;
    backdrop-filter: blur(24px) saturate(150%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(150%) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.3) !important;
    box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05) !important;
    border-radius: 8px !important;
    transition: all 0.3s ease;
}}

/* 4. Proxies 页面：已选中的代理节点 (提亮并保留原生左边框) */
.base-content .MuiListItemButton-root.Mui-selected {{
    background-color: rgba(255, 255, 255, 0.25) !important;
    background-image: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
    backdrop-filter: blur(24px) saturate(150%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(150%) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.3) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2) !important;
    box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1) !important;
    border-radius: 8px !important;
    transition: all 0.3s ease;
}}

/* =========================================
   暗黑模式适配
   ========================================= */
html.dark .MuiPaper-root, body.dark .MuiPaper-root, [data-theme="dark"] .MuiPaper-root,
html.dark .MuiCard-root, body.dark .MuiCard-root, [data-theme="dark"] .MuiCard-root,
html.dark .card, body.dark .card, [data-theme="dark"] .card,
html.dark .base-content div[class*="MuiGrid"] > .MuiBox-root,
html.dark .base-content div[class*="MuiGrid"] > div[class*="MuiGrid"] > .MuiBox-root,
html.dark .base-content > div > div[class*="MuiGrid"] > div[class*="MuiGrid"] > .MuiBox-root,
html.dark .base-content .MuiListItemButton-root:not(.Mui-selected) {{
    background-color: rgba(0, 0, 0, 0.15) !important;
    background-image: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.0) 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.15) !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
}}

html.dark .base-content .MuiListItemButton-root.Mui-selected {{
    background-color: rgba(255, 255, 255, 0.15) !important;
    background-image: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.0) 100%) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
}}

@media (prefers-color-scheme: dark) {{
    .MuiPaper-root, .MuiCard-root, .MuiDialog-paper, .MuiDrawer-paper, .MuiMenu-paper, 
    .card, .panel, .wrapper,
    .base-content div[class*="MuiGrid"] > .MuiBox-root,
    .base-content div[class*="MuiGrid"] > div[class*="MuiGrid"] > .MuiBox-root,
    .base-content > div > div[class*="MuiGrid"] > div[class*="MuiGrid"] > .MuiBox-root,
    .base-content .MuiListItemButton-root:not(.Mui-selected) {{
        background-color: rgba(0, 0, 0, 0.15) !important;
        background-image: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.0) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    }}

    .base-content .MuiListItemButton-root.Mui-selected {{
        background-color: rgba(255, 255, 255, 0.15) !important;
        background-image: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.0) 100%) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    }}
}}"""
            log("CSS generated successfully.")
            return css
            
        except Exception as e:
            log(f"Error generating CSS: {traceback.format_exc()}")
            raise e

    def update_theme_setting(self, css_str):
        if 'theme_setting' not in self.config_data or not isinstance(self.config_data['theme_setting'], dict):
            self.config_data['theme_setting'] = {}
            
        self.config_data['theme_setting']['css_injection'] = css_str
        self.save_config()

    def apply_background(self):
        if not self.selected_image_path:
            messagebox.showwarning("提示", "请先选择一张图片。")
            return
            
        try:
            css_str = self.generate_css(self.selected_image_path, self.opacity.get())
            self.update_theme_setting(css_str)
        except Exception as e:
            log(f"Error in apply_background: {traceback.format_exc()}")
            messagebox.showerror("错误", f"处理图片或生成 CSS 时出错:\n{e}")

    def clear_background(self):
        try:
            if 'theme_setting' in self.config_data and isinstance(self.config_data['theme_setting'], dict):
                if 'css_injection' in self.config_data['theme_setting']:
                    del self.config_data['theme_setting']['css_injection']
                    if not self.config_data['theme_setting']:
                        self.config_data['theme_setting'] = None
                    self.save_config()
                    
                    self.lbl_path.config(text="未选择图片", fg="gray")
                    self.lbl_preview.config(image='', text="图片预览区", width=40, height=10)
                    self.selected_image_path = None
                    self.preview_image = None
                    self.root.geometry("450x350")
                    log("Background cleared.")
                    return
            
            messagebox.showinfo("提示", "当前并未设置任何自定义背景。")
        except Exception as e:
            log(f"Error in clear_background: {traceback.format_exc()}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        if os.name != 'nt':
            root.lift()
            root.attributes('-topmost', True)
            root.after_idle(root.attributes, '-topmost', False)
        app = App(root)
        root.mainloop()
    except Exception as e:
        log(f"Fatal error: {traceback.format_exc()}")

