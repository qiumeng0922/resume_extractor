# 在 Mac 上编译 Windows EXE 指南

## 📋 概述

Mac 无法直接安装 Windows 子系统（WSL 是 Windows 专有功能）。要在 Mac 上编译 Windows exe 文件，有以下几种方案：

---

## 🎯 方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **虚拟机** | 完全控制，可调试 | 需要购买软件，占用资源 | ⭐⭐⭐⭐⭐ |
| **GitHub Actions** | 免费，自动化 | 需要 GitHub 账号 | ⭐⭐⭐⭐ |
| **云服务器** | 灵活 | 需要付费 | ⭐⭐⭐ |
| **Wine** | 免费 | 兼容性差，不推荐 | ⭐ |

---

## 🖥️ 方案 1：使用虚拟机（最推荐）

### 步骤 1：安装虚拟机软件

**选项 A：Parallels Desktop**（推荐，性能最好）
- 官网：https://www.parallels.com/
- 价格：约 ¥498/年
- 优点：性能优秀，与 macOS 集成好

**选项 B：VMware Fusion**
- 官网：https://www.vmware.com/products/fusion.html
- 价格：约 $199
- 优点：稳定可靠

**选项 C：VirtualBox**（免费）
- 官网：https://www.virtualbox.org/
- 价格：免费
- 优点：免费开源
- 缺点：性能较差

### 步骤 2：安装 Windows

1. 下载 Windows 10/11 ISO 镜像
2. 在虚拟机中安装 Windows
3. 安装必要的驱动和工具

### 步骤 3：在 Windows 中编译 EXE

```bash
# 1. 安装 Python 3.10+
# 2. 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 3. 编译 EXE（使用 spec 文件）
cd "5.界面/条件较为简单+多行表"
pyinstaller build_exe.spec

# 或者直接使用命令
pyinstaller --onefile --name "AI简历初筛系统" --add-data "data;data" backend.py
```

---

## ☁️ 方案 2：使用 GitHub Actions（免费自动化）

### 优点
- ✅ 完全免费
- ✅ 无需本地安装 Windows
- ✅ 自动化构建
- ✅ 可以设置自动发布

### 使用步骤

1. **将项目推送到 GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <你的GitHub仓库地址>
   git push -u origin main
   ```

2. **触发构建**
   - 方式 1：在 GitHub 网页上，进入 Actions 标签，手动运行工作流
   - 方式 2：推送版本标签自动触发
     ```bash
     git tag v1.0.0
     git push origin v1.0.0
     ```

3. **下载构建结果**
   - 在 Actions 页面找到完成的构建
   - 下载 Artifacts 中的 exe 文件

### 工作流文件位置

已创建：`.github/workflows/build-windows-exe.yml`

---

## 🚀 方案 3：使用云服务器

### 推荐服务
- **AWS EC2**：按需付费
- **Azure VM**：有免费额度
- **腾讯云/阿里云**：国内访问快

### 步骤
1. 创建 Windows 云服务器实例
2. 远程连接（RDP）
3. 安装 Python 和依赖
4. 编译 exe
5. 下载到本地

---

## 📝 PyInstaller 配置说明

### 基本命令

```bash
# 单文件模式（推荐）
pyinstaller --onefile --name "AI简历初筛系统" backend.py

# 包含数据文件
pyinstaller --onefile --name "AI简历初筛系统" --add-data "data;data" backend.py

# 使用 spec 文件（更灵活）
pyinstaller build_exe.spec
```

### 常用参数

- `--onefile`：打包成单个 exe 文件
- `--name`：指定输出文件名
- `--add-data`：包含数据文件（Windows 用 `;` 分隔，Mac/Linux 用 `:`）
- `--hidden-import`：包含隐藏导入的模块
- `--console`：显示控制台窗口
- `--noconsole`：不显示控制台（GUI 应用）
- `--icon`：指定图标文件

### 已创建的配置文件

- `build_exe.spec`：PyInstaller 配置文件，可以自定义打包选项

---

## ⚠️ 注意事项

### 1. 路径问题
- Windows 和 Mac 的路径分隔符不同（`\` vs `/`）
- 使用 `os.path.join()` 处理路径

### 2. 编码问题
- 确保所有文件使用 UTF-8 编码
- 在代码中明确指定编码

### 3. 依赖问题
- 某些 Python 包可能在不同平台有不同行为
- 建议在 Windows 环境中测试

### 4. 文件大小
- 使用 `--onefile` 会生成较大的 exe 文件
- 首次运行可能较慢（需要解压）

---

## 🔧 故障排查

### 问题 1：找不到模块
```bash
# 添加隐藏导入
pyinstaller --hidden-import=模块名 backend.py
```

### 问题 2：找不到数据文件
```bash
# 确保使用正确的路径分隔符
# Windows: --add-data "data;data"
# Mac/Linux: --add-data "data:data"
```

### 问题 3：exe 文件太大
- 使用 `--exclude-module` 排除不需要的模块
- 考虑使用 `--onedir` 模式（多文件）

---

## 📚 参考资源

- [PyInstaller 官方文档](https://pyinstaller.org/)
- [Parallels Desktop](https://www.parallels.com/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)

---

## 💡 推荐方案

**对于你的项目，我推荐：**

1. **短期/一次性**：使用 GitHub Actions（免费，无需配置）
2. **长期/频繁使用**：使用 Parallels Desktop + Windows 虚拟机
3. **预算有限**：使用 VirtualBox（免费）+ Windows

---

**创建时间**：2026-01-20  
**适用项目**：AI简历初筛系统
