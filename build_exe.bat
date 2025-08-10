@echo off
echo 正在打包 txt2epub GUI 应用为 exe...
echo.

REM 检查 Python 是否可用
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python。请确保已安装 Python 并添加到系统路径。
    pause
    exit /b 1
)

REM 运行打包脚本
python build_exe.py

echo.
echo 打包完成！
echo 生成的 exe 文件位于 dist 目录中。
echo.
pause