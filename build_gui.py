import sys
import os
from pathlib import Path

def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['txt2epub_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('utils', 'utils'), ('icons', 'icons')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='txt2epub_gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icons/app.png'
)
'''
    
    with open('txt2epub_gui.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("已创建打包配置文件 txt2epub_gui.spec")

def create_build_script():
    """创建打包脚本"""
    build_script = '''# 打包脚本
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
'''
    
    with open('build_exe.py', 'w', encoding='utf-8') as f:
        f.write(build_script)
    
    print("已创建打包脚本 build_exe.py")

def update_pyproject():
    """更新pyproject.toml，添加GUI应用入口"""
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.exists():
        content = pyproject_path.read_text(encoding='utf-8')
        if 'txt2epub_gui = "txt2epub_gui:main"' not in content:
            # 在合适的位置插入GUI应用入口
            if '[project.scripts]' in content:
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    if '[project.scripts]' in line:
                        lines.insert(i+1, 'txt2epub_gui = "txt2epub_gui:main"')
                        break
                content = '\n'.join(lines)
            else:
                content += '\n[project.scripts]\ntxt2epub_gui = "txt2epub_gui:main"\n'
            
            pyproject_path.write_text(content, encoding='utf-8')
            print("已更新 pyproject.toml，添加GUI应用入口")

def main():
    create_spec_file()
    create_build_script()
    update_pyproject()
    print("打包配置文件创建完成！")
    print("运行以下命令进行打包:")
    print("  python build_exe.py")

if __name__ == "__main__":
    main()