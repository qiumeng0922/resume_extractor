# GitHub Actions 打包 Windows EXE 使用指南

## 🎯 概述

使用 GitHub Actions 可以在 Mac 上自动打包 Windows exe 文件，无需本地 Windows 环境！

## ✅ 优势

- ✅ **完全免费** - GitHub Actions 提供免费额度
- ✅ **无需 Windows** - 在 Mac 上操作即可
- ✅ **自动化** - 一键触发，自动打包
- ✅ **可重复** - 随时可以重新打包
- ✅ **版本管理** - 可以设置版本标签自动打包

## 🚀 快速开始

### 步骤 1：将项目推送到 GitHub

如果项目还没有推送到 GitHub：

```bash
# 在项目根目录执行
cd "/Users/ameng/Documents/projects/11.AI简历可行性评估"

# 初始化git（如果还没有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "准备使用GitHub Actions打包"

# 在GitHub上创建新仓库，然后添加远程地址
git remote add origin https://github.com/你的用户名/你的仓库名.git

# 推送到GitHub
git push -u origin main
```

### 步骤 2：触发自动打包

1. **打开 GitHub 网页**
   - 访问你的仓库：`https://github.com/你的用户名/你的仓库名`

2. **进入 Actions 标签**
   - 点击仓库顶部的 **Actions** 标签

3. **选择工作流**
   - 在左侧找到 **"构建 Windows EXE"** 工作流
   - 点击进入

4. **手动触发**
   - 点击右侧的 **"Run workflow"** 按钮
   - 选择分支（通常是 `main` 或 `master`）
   - 点击绿色的 **"Run workflow"** 按钮

5. **等待构建完成**
   - 点击运行中的工作流查看进度
   - 通常需要 5-10 分钟
   - 等待所有步骤显示 ✅

### 步骤 3：下载打包结果

1. **找到完成的构建**
   - 在 Actions 页面找到显示 ✅ 的构建
   - 点击进入查看详情

2. **下载 Artifacts**
   - 滚动到页面底部
   - 找到 **Artifacts** 部分
   - 有两个下载选项：
     - **windows-exe-standalone** - 单独的 exe 文件
     - **windows-deployment-package** - 完整的部署包（包含目录结构）

3. **解压使用**
   - 下载 zip 文件
   - 解压后即可使用

## 📦 下载内容说明

### windows-exe-standalone
```
AI简历初筛系统.exe  # 单独的exe文件
```

### windows-deployment-package（推荐）
```
部署包/
├── AI简历初筛系统.exe    # 主程序
├── data/                  # 数据目录（已创建）
├── output/                # 输出目录（已创建）
└── logs/                  # 日志目录（已创建）
```

**推荐下载** `windows-deployment-package`，因为已经创建好了目录结构。

## 🔄 自动触发（可选）

除了手动触发，还可以通过推送版本标签自动触发：

```bash
# 创建版本标签
git tag v1.0.0

# 推送标签到GitHub
git push origin v1.0.0
```

推送标签后，GitHub Actions 会自动开始构建。

## 📋 工作流配置说明

工作流文件位置：`.github/workflows/build-windows-exe.yml`

### 构建步骤：

1. ✅ 检出代码
2. ✅ 设置 Python 3.10
3. ✅ 安装项目依赖
4. ✅ 安装 PyInstaller
5. ✅ 使用 `build_exe.spec` 打包
6. ✅ 创建部署包目录结构
7. ✅ 上传构建产物

### 构建环境：

- **操作系统**：Windows Latest
- **Python版本**：3.10
- **打包工具**：PyInstaller

## ⚠️ 注意事项

### 1. 文件大小限制

- GitHub Actions Artifacts 有大小限制（通常 10GB）
- 如果 exe 文件太大，可能需要优化

### 2. 构建时间

- 首次构建可能需要 10-15 分钟
- 后续构建通常 5-10 分钟
- 免费账户有构建时间限制（每月 2000 分钟）

### 3. 保留时间

- Artifacts 默认保留 30 天
- 建议及时下载

### 4. 私有仓库

- 私有仓库也可以使用 GitHub Actions
- 免费账户每月有 2000 分钟构建时间

## 🔍 故障排查

### 问题 1：工作流没有运行

**检查项**：
- 确保 `.github/workflows/build-windows-exe.yml` 文件存在
- 确保文件已提交到 GitHub
- 检查文件格式是否正确（YAML 格式）

### 问题 2：构建失败

**查看日志**：
- 点击失败的构建
- 查看每个步骤的日志
- 常见问题：
  - 依赖安装失败 → 检查 `requirements.txt`
  - 打包失败 → 检查 `build_exe.spec` 配置
  - 路径错误 → 检查文件路径是否正确

### 问题 3：找不到 Artifacts

**可能原因**：
- 构建还在进行中（等待完成）
- 构建失败（检查错误日志）
- 已过期（超过 30 天）

## 📝 使用示例

### 示例 1：首次打包

```bash
# 1. 提交代码到GitHub
git add .
git commit -m "添加打包配置"
git push

# 2. 在GitHub网页上手动触发构建

# 3. 等待构建完成，下载exe文件
```

### 示例 2：更新后重新打包

```bash
# 1. 修改代码
# ... 修改文件 ...

# 2. 提交并推送
git add .
git commit -m "更新功能"
git push

# 3. 在GitHub Actions中重新运行工作流
```

### 示例 3：版本发布

```bash
# 1. 完成开发，准备发布
git add .
git commit -m "v1.0.0 发布版本"
git push

# 2. 创建版本标签（自动触发构建）
git tag v1.0.0
git push origin v1.0.0

# 3. GitHub Actions 自动开始构建
# 4. 构建完成后下载发布版本
```

## 🎉 总结

使用 GitHub Actions 是在 Mac 上打包 Windows exe 的最佳方案：

1. ✅ **简单** - 只需推送代码，点击按钮
2. ✅ **免费** - 无需额外成本
3. ✅ **可靠** - 使用官方 Windows 环境
4. ✅ **自动化** - 可以设置自动触发

**现在就开始使用吧！** 🚀

---

**相关文件**：
- `.github/workflows/build-windows-exe.yml` - 工作流配置
- `build_exe.spec` - PyInstaller 配置
- `部署包使用说明.md` - 最终用户使用指南
