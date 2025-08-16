import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import argparse
import sys
from pathlib import Path
import os
import ctypes

# 启用高DPI支持
try:
    # Windows环境下启用高DPI支持
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

from utils.logger import setup_logger
from utils.txt_reader import read_txt, detect_encoding
from utils.epub_builder import build_epub

# 尝试导入PIL用于图片处理
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

log = setup_logger(__name__)
if not PIL_AVAILABLE:
    log.warning("未安装PIL库，封面预览功能将不可用")

class Txt2EpubGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TXT转EPUB工具")

        self.root.geometry("900x700")
        self.root.minsize(900, 700)
        self.root.resizable(True, True)
        
        # 设置图标
        self.set_app_icon()
        
        # 定义字体 - 根据DPI调整字体大小
        self.default_font = ('宋体', 10)
        self.title_font = ('宋体', 12, 'bold')
        
        # 检查DPI并调整字体大小
        self.adjust_for_dpi()
        
        # 变量
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.title = tk.StringVar()
        self.author = tk.StringVar(value="作者未知")
        self.cover_path = tk.StringVar()
        self.encoding = tk.StringVar()
        self.debug_mode = tk.BooleanVar()
        self.disable_clean = tk.BooleanVar()  # 文本净化选项
        
        # 常见编码列表
        self.common_encodings = ['自动检测', 'UTF-8', 'GBK', 'GB2312', 'BIG5', 'UTF-16']
        self.selected_encoding = tk.StringVar(value='自动检测')
        
        # 封面预览相关变量
        self.cover_image = None
        self.cover_photo = None
        
        self.create_widgets()
        self.configure_styles()
        
    def adjust_for_dpi(self):
        """根据屏幕DPI调整字体大小"""
        try:
            # 获取窗口的DPI
            if sys.platform == "win32":
                hdc = ctypes.windll.user32.GetDC(0)
                dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
                ctypes.windll.user32.ReleaseDC(0, hdc)
                
                # 根据标准DPI (96) 计算缩放因子
                scale_factor = dpi / 96.0
                
                # 调整字体大小
                if scale_factor > 1.0:
                    base_size = 10
                    title_size = 12
                    self.default_font = ('宋体', int(base_size * scale_factor))
                    self.title_font = ('宋体', int(title_size * scale_factor), 'bold')
        except Exception as e:
            log.debug(f"DPI调整失败: {e}")
            # 使用默认字体设置
            self.default_font = ('宋体', 10)
            self.title_font = ('宋体', 12, 'bold')
        
    def set_app_icon(self):
        """设置应用程序图标"""
        try:
            # 尝试设置图标
            if getattr(sys, 'frozen', False):
                # 如果是打包后的exe
                application_path = os.path.dirname(sys.executable)
            else:
                # 如果是脚本运行
                application_path = os.path.dirname(os.path.abspath(__file__))
                
            icon_path = os.path.join(application_path, "icons", "app.png")
            if os.path.exists(icon_path):
                # 对于PNG图标，需要使用PhotoImage而不是iconbitmap
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
        except Exception as e:
            log.debug(f"设置图标失败: {e}")
            # 设置默认图标
            pass

    def configure_styles(self):
        """配置界面样式"""
        self.style = ttk.Style()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="TXT转EPUB电子书工具", font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 输入文件选择
        ttk.Label(main_frame, text="TXT文件:", font=self.default_font).grid(row=1, column=0, sticky=tk.W, pady=5)
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        input_frame.columnconfigure(0, weight=1)
        ttk.Entry(input_frame, textvariable=self.input_path, font=self.default_font).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(input_frame, text="浏览...", command=self.browse_input).grid(row=0, column=1)
        
        # 输出文件选择
        ttk.Label(main_frame, text="EPUB文件:", font=self.default_font).grid(row=2, column=0, sticky=tk.W, pady=5)
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(0, weight=1)
        ttk.Entry(output_frame, textvariable=self.output_path, font=self.default_font).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="浏览...", command=self.browse_output).grid(row=0, column=1)
        
        # 标题
        ttk.Label(main_frame, text="书籍标题:", font=self.default_font).grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.title, font=self.default_font).grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 作者
        ttk.Label(main_frame, text="作者:", font=self.default_font).grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.author, font=self.default_font).grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 封面
        ttk.Label(main_frame, text="封面图片:", font=self.default_font).grid(row=5, column=0, sticky=tk.W, pady=5)
        cover_frame = ttk.Frame(main_frame)
        cover_frame.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        cover_frame.columnconfigure(0, weight=1)
        ttk.Entry(cover_frame, textvariable=self.cover_path, font=self.default_font).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(cover_frame, text="浏览...", command=self.browse_cover).grid(row=0, column=1)
        
        # 封面预览区域
        self.cover_preview_frame = ttk.LabelFrame(main_frame, text="封面预览", padding="5")
        self.cover_preview_frame.grid(row=6, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.cover_preview_frame.columnconfigure(0, weight=1)
        self.cover_preview_frame.rowconfigure(0, weight=1)
        
        self.cover_preview_label = ttk.Label(self.cover_preview_frame)
        self.cover_preview_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 隐藏预览区域直到选择图片
        self.cover_preview_frame.grid_remove()
        
        # 编码
        ttk.Label(main_frame, text="文件编码:", font=self.default_font).grid(row=7, column=0, sticky=tk.W, pady=5)
        encoding_frame = ttk.Frame(main_frame)
        encoding_frame.grid(row=7, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        encoding_frame.columnconfigure(0, weight=1)
        ttk.Combobox(encoding_frame, textvariable=self.selected_encoding, values=self.common_encodings, state="readonly", font=self.default_font).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Label(main_frame, text="选择文件编码格式", font=('Arial', 8, 'italic')).grid(row=8, column=1, sticky=tk.W, pady=(0, 10))
        
        # 调试模式
        ttk.Checkbutton(main_frame, text="调试模式", variable=self.debug_mode).grid(row=9, column=0, sticky=tk.W, pady=5)
        
        # 文本净化选项
        ttk.Checkbutton(main_frame, text="禁用文本净化", variable=self.disable_clean).grid(row=9, column=1, sticky=tk.W, pady=5)
        
        # 日志文本框
        ttk.Label(main_frame, text="处理日志:", font=self.default_font).grid(row=10, column=0, sticky=tk.W, pady=(10, 5))
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=11, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.log_text = tk.Text(log_frame, height=18, font=self.default_font)
        log_scroll_y = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scroll_x = ttk.Scrollbar(log_frame, orient=tk.HORIZONTAL, command=self.log_text.xview)
        self.log_text.configure(yscrollcommand=log_scroll_y.set, xscrollcommand=log_scroll_x.set)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        log_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=12, column=0, columnspan=3, pady=15)
        ttk.Button(button_frame, text="开始转换", command=self.convert).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="退出程序", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        # 配置主框架的行权重
        main_frame.rowconfigure(11, weight=1)
        
    def browse_input(self):
        # 保存当前窗口状态
        self.root.update_idletasks()
        filename = filedialog.askopenfilename(
            title="选择TXT文件",
            filetypes=[("TXT文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filename:
            self.input_path.set(filename)
            # 如果没有设置标题，则使用文件名（不含扩展名）
            if not self.title.get():
                self.title.set(Path(filename).stem)
            # 如果没有设置输出路径，则使用输入路径加上.epub扩展名
                if not self.output_path.get():
                    self.output_path.set(str(Path(filename).with_suffix('.epub')))
                
    def browse_output(self):
        # 保存当前窗口状态
        self.root.update_idletasks()
        filename = filedialog.asksaveasfilename(
            title="保存EPUB文件",
            defaultextension=".epub",
            filetypes=[("EPUB文件", "*.epub"), ("所有文件", "*.*")]
        )
        if filename:
            self.output_path.set(filename)
            
    def browse_cover(self):
        # 保存当前窗口状态
        self.root.update_idletasks()
        filename = filedialog.askopenfilename(
            title="选择封面图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png"), ("所有文件", "*.*")]
        )
        if filename:
            self.cover_path.set(filename)
            self.show_cover_preview(filename)
            
    def show_cover_preview(self, image_path):
        """显示封面预览"""
        # 如果PIL不可用，直接返回
        if not PIL_AVAILABLE:
            self.cover_preview_frame.grid_remove()
            return
            
        try:
            from PIL import Image, ImageTk
            
            # 显示预览区域
            self.cover_preview_frame.grid()
            
            # 打开并调整图片大小以适应预览区域
            image = Image.open(image_path)
            
            # 计算合适的预览尺寸
            max_width = 300
            max_height = 200
            
            # 计算缩放比例
            ratio = min(max_width/image.width, max_height/image.height)
            new_width = int(image.width * ratio)
            new_height = int(image.height * ratio)
            
            # 调整图片大小
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为Tkinter可用的图片格式
            self.cover_photo = ImageTk.PhotoImage(resized_image)
            
            # 更新预览标签
            self.cover_preview_label.configure(image=self.cover_photo)
            self.cover_preview_label.image = self.cover_photo  # 保持引用以防止被垃圾回收
            
        except Exception as e:
            log.debug(f"显示封面预览失败: {e}")
            # 隐藏预览区域
            self.cover_preview_frame.grid_remove()
            
    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def convert(self):
        try:
            # 获取输入参数
            input_file = self.input_path.get()
            if not input_file:
                messagebox.showerror("错误", "请选择输入文件")
                return
                
            input_path = Path(input_file)
            if not input_path.is_file():
                messagebox.showerror("错误", f"输入文件不存在: {input_file}")
                return
                
            # 设置日志级别
            if self.debug_mode.get():
                log.setLevel('DEBUG')
                
            # 检测编码
            self.log_message("=" * 50)
            self.log_message("开始转换...")
            
            # 使用用户选择的编码或自动检测
            if self.selected_encoding.get() == '自动检测':
                self.log_message("检测文件编码...")
                enc, confidence = detect_encoding(input_path)
                self.log_message(f"检测到的文件编码: {enc} (置信度: {confidence:.2f})")
            elif self.selected_encoding.get():
                enc = self.selected_encoding.get()
                self.log_message(f"使用指定编码: {enc}")
            else:
                enc = self.encoding.get() or detect_encoding(input_path)[0]
                self.log_message(f"文件编码: {enc}")
            
            # 读取文本
            self.log_message("读取文本...")
            # 如果用户禁用了文本净化功能，则传入空列表作为clean_rules参数
            clean_rules = [] if self.disable_clean.get() else None
            lines = read_txt(input_path, enc, split_include_title=True, clean_rules=clean_rules)
            
            if not lines:
                self.log_message("文件为空或无法读取文本")
                messagebox.showerror("错误", "文件为空或无法读取文本")
                return
                
            # 生成 EPUB
            title = self.title.get() or input_path.stem
            output_path = self.output_path.get() or str(input_path.with_suffix('.epub'))
            output_path = Path(output_path)
            
            self.log_message("生成 EPUB...")
            cover_img = Path(self.cover_path.get()) if self.cover_path.get() else None
            
            build_epub(
                title=title,
                author=self.author.get(),
                chapters=lines,
                output_path=output_path,
                cover_img=cover_img
            )
            
            self.log_message(f"完成: {output_path}")
            messagebox.showinfo("成功", f"EPUB文件已生成:{output_path}")
            
        except Exception as e:
            self.log_message(f"转换过程中出错: {str(e)}")
            messagebox.showerror("错误", f"转换过程中出错: {str(e)}")

def main():
    root = tk.Tk()
    app = Txt2EpubGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()