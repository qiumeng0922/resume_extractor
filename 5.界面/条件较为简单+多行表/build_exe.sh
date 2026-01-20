#!/bin/bash
# AI简历初筛系统 - Mac/Linux 打包脚本
# 注意：此脚本只能打包Mac/Linux版本，无法打包Windows exe

echo "========================================"
echo "AI简历初筛系统 - 打包脚本"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3，请先安装Python 3.10+"
    exit 1
fi

echo "[1/4] 检查依赖..."
python3 -m pip install --upgrade pip > /dev/null 2>&1
python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[错误] 依赖安装失败"
    exit 1
fi

echo ""
echo "[2/4] 安装PyInstaller..."
python3 -m pip install pyinstaller
if [ $? -ne 0 ]; then
    echo "[错误] PyInstaller安装失败"
    exit 1
fi

echo ""
echo "⚠️  重要提示："
echo "   在Mac/Linux上无法直接打包Windows exe文件"
echo "   如需Windows版本，请："
echo "   1. 在Windows电脑上运行 build_exe.bat"
echo "   2. 或使用GitHub Actions自动打包（.github/workflows/build-windows-exe.yml）"
echo ""
read -p "是否继续打包Mac版本？(y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "[3/4] 开始打包（这可能需要几分钟）..."
python3 -m PyInstaller build_exe.spec --clean
if [ $? -ne 0 ]; then
    echo "[错误] 打包失败，请检查错误信息"
    exit 1
fi

echo ""
echo "[4/4] 整理部署包..."
if [ -f "dist/AI简历初筛系统" ] || [ -f "dist/AI简历初筛系统.app" ]; then
    # 创建部署目录
    mkdir -p "部署包"
    
    # 复制可执行文件
    if [ -f "dist/AI简历初筛系统" ]; then
        cp "dist/AI简历初筛系统" "部署包/"
    elif [ -f "dist/AI简历初筛系统.app" ]; then
        cp -r "dist/AI简历初筛系统.app" "部署包/"
    fi
    
    # 创建必要的目录
    mkdir -p "部署包/data"
    mkdir -p "部署包/output"
    mkdir -p "部署包/logs"
    
    echo ""
    echo "========================================"
    echo "✅ 打包完成！"
    echo "========================================"
    echo ""
    echo "📦 部署包位置: 部署包/"
    echo "📄 可执行文件: AI简历初筛系统 (或 .app)"
    echo ""
    echo "💡 注意：这是Mac/Linux版本，不是Windows exe"
    echo ""
else
    echo "[错误] 未找到生成的可执行文件"
    exit 1
fi
