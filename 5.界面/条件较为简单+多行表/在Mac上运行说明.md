# 在 Mac 上运行 AI简历初筛系统

## ⚠️ 重要提示

**Windows EXE 文件无法在 Mac 上直接运行！**

EXE 文件是 Windows 专用的可执行文件，Mac 无法直接运行。但你可以：

## 🚀 方案 1：在 Mac 上直接运行 Python 源代码（推荐）

项目本身就是 Python 项目，可以直接在 Mac 上运行，无需打包的 EXE 文件。

### 步骤 1：检查 Python 环境

```bash
# 检查 Python 版本（需要 3.10+）
python3 --version

# 如果没有 Python，安装它
# Mac 通常自带 Python 3，如果没有：
# brew install python3
```

### 步骤 2：安装依赖

```bash
# 进入项目目录
cd "/Users/ameng/Documents/projects/11.AI简历可行性评估/5.界面/条件较为简单+多行表"

# 安装依赖
pip3 install -r requirements.txt
```

### 步骤 3：运行程序

```bash
# 直接运行 backend.py
python3 backend.py
```

### 步骤 4：使用程序

1. 程序会自动启动后端服务
2. 浏览器会自动打开：http://127.0.0.1:8000
3. 如果浏览器没有自动打开，手动访问上述地址
4. 上传文件开始使用

---

## 🖥️ 方案 2：使用虚拟机运行 Windows EXE

如果你想使用打包好的 EXE 文件，需要在 Mac 上安装 Windows 虚拟机。

### 推荐虚拟机软件：

1. **Parallels Desktop**（性能最好）
   - 官网：https://www.parallels.com/
   - 价格：约 ¥498/年
   - 优点：性能优秀，与 macOS 集成好

2. **VMware Fusion**
   - 官网：https://www.vmware.com/products/fusion.html
   - 价格：约 $199
   - 优点：稳定可靠

3. **VirtualBox**（免费）
   - 官网：https://www.virtualbox.org/
   - 价格：免费
   - 优点：免费开源
   - 缺点：性能较差

### 使用步骤：

1. 安装虚拟机软件
2. 在虚拟机中安装 Windows 10/11
3. 将 EXE 文件复制到虚拟机中
4. 在虚拟机中运行 EXE 文件

---

## 🍷 方案 3：使用 Wine（不推荐）

Wine 可以在 Mac 上运行部分 Windows 程序，但兼容性较差。

```bash
# 安装 Wine
brew install --cask wine-stable

# 尝试运行（可能不工作）
wine AI简历初筛系统.exe
```

**注意**：Wine 对复杂的 Python 打包程序支持不好，很可能无法运行。

---

## 📝 推荐方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **直接运行 Python** | 简单、快速、无需额外软件 | 需要安装 Python 和依赖 | ⭐⭐⭐⭐⭐ |
| **虚拟机** | 可以使用 EXE 文件 | 需要购买软件、占用资源 | ⭐⭐⭐ |
| **Wine** | 免费 | 兼容性差、可能无法运行 | ⭐ |

---

## 🎯 快速开始（推荐）

### 在 Mac 上直接运行：

```bash
# 1. 进入项目目录
cd "/Users/ameng/Documents/projects/11.AI简历可行性评估/5.界面/条件较为简单+多行表"

# 2. 安装依赖（如果还没安装）
pip3 install -r requirements.txt

# 3. 运行程序
python3 backend.py
```

就这么简单！程序会自动：
- ✅ 启动后端服务
- ✅ 打开浏览器界面
- ✅ 可以上传文件进行筛选

---

## 💡 为什么推荐直接运行 Python？

1. **更简单**：无需安装虚拟机或 Wine
2. **更快速**：直接运行，无需启动虚拟机
3. **更灵活**：可以修改代码、调试
4. **更稳定**：原生运行，不会有兼容性问题

---

## 📦 EXE 文件的用途

EXE 文件主要用于：
- ✅ 在没有 Python 环境的 Windows 电脑上运行
- ✅ 分发给其他 Windows 用户
- ✅ 生产环境部署

对于 Mac 用户，直接运行 Python 源代码更方便！

---

**总结**：在 Mac 上，直接运行 `python3 backend.py` 即可，无需使用 EXE 文件！🚀
