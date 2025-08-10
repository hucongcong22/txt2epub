# 打包脚本
import subprocess
import sys
import os

def install_pyinstaller():
    """安装PyInstaller"""
    try:
        import PyInstaller
        print("PyInstaller 已安装")
    except ImportError:
        print("正在安装 PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller"])

def build_exe():
    """构建exe文件"""
    install_pyinstaller()
    
    # 构建命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--windowed",  # GUI应用，不显示控制台
        "--name", "txt2epub_gui",
        "--icon", "icons/app.png",
        "--add-data", "utils;utils",
        "--add-data", "icons;icons",
        "txt2epub_gui.py"
    ]
    
    print("执行打包命令:", " ".join(cmd))
    subprocess.run(cmd)

if __name__ == "__main__":
    build_exe()
