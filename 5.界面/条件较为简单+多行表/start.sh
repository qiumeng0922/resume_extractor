#!/bin/bash
# AI简历初筛系统启动脚本

echo "=========================================="
echo "🚀 启动 AI简历初筛系统"
echo "=========================================="
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python"
    exit 1
fi

# 检查依赖是否安装
echo "📦 检查依赖包..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  检测到缺少依赖包，正在安装..."
    pip3 install -r requirements.txt
fi

echo ""
echo "✅ 依赖检查完成"
echo ""
echo "📍 后端服务将启动在: http://127.0.0.1:8000"
echo "📖 API 文档地址: http://127.0.0.1:8000/docs"
echo ""
echo "💡 提示: 在浏览器中打开 index.html 使用前端界面"
echo ""
echo "=========================================="
echo ""

# 启动后端服务
python3 backend.py
