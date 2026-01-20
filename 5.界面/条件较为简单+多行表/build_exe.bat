@echo off
chcp 65001 >nul
echo ========================================
echo AI简历初筛系统 - Windows EXE 打包脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.10+
    pause
    exit /b 1
)

echo [1/4] 检查依赖...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo.
echo [2/4] 安装PyInstaller...
python -m pip install pyinstaller
if errorlevel 1 (
    echo [错误] PyInstaller安装失败
    pause
    exit /b 1
)

echo.
echo [3/4] 开始打包（这可能需要几分钟）...
pyinstaller build_exe.spec --clean
if errorlevel 1 (
    echo [错误] 打包失败，请检查错误信息
    pause
    exit /b 1
)

echo.
echo [4/4] 整理部署包...
if exist "dist\AI简历初筛系统.exe" (
    REM 创建部署目录
    if not exist "部署包" mkdir "部署包"
    
    REM 复制exe文件
    copy "dist\AI简历初筛系统.exe" "部署包\" >nul
    
    REM 创建data目录（用于存放用户上传的文件解析结果）
    if not exist "部署包\data" mkdir "部署包\data"
    
    REM 创建output目录（用于存放筛选结果）
    if not exist "部署包\output" mkdir "部署包\output"
    
    REM 创建logs目录（用于存放日志）
    if not exist "部署包\logs" mkdir "部署包\logs"
    
    echo.
    echo ========================================
    echo ✅ 打包完成！
    echo ========================================
    echo.
    echo 📦 部署包位置: 部署包\
    echo 📄 可执行文件: AI简历初筛系统.exe
    echo.
    echo 💡 使用说明:
    echo    1. 将"部署包"文件夹复制到目标Windows电脑
    echo    2. 双击运行"AI简历初筛系统.exe"
    echo    3. 浏览器会自动打开 http://127.0.0.1:8000
    echo    4. 上传简历和岗位文件开始筛选
    echo.
) else (
    echo [错误] 未找到生成的exe文件
    pause
    exit /b 1
)

pause
