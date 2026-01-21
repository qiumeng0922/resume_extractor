# 设置 GitHub 仓库 - 快速指南

## 📋 当前状态

✅ 代码已提交到本地 git  
❌ 还没有 GitHub 远程仓库

## 🚀 下一步：设置 GitHub 仓库

### 方法 1：在 GitHub 网页上创建（推荐）

#### 步骤 1：创建 GitHub 仓库

1. **打开 GitHub**
   - 访问：https://github.com
   - 登录你的账号（如果没有账号，先注册）

2. **创建新仓库**
   - 点击右上角的 **"+"** 按钮
   - 选择 **"New repository"**

3. **填写仓库信息**
   - **Repository name**: `AI简历可行性评估` 或 `resume-screening-system`
   - **Description**: `AI简历初筛系统 - Windows EXE打包`
   - **Visibility**: 
     - 选择 **Public**（公开，免费使用 GitHub Actions）
     - 或 **Private**（私有，需要付费账户才能使用 GitHub Actions）
   - **不要**勾选 "Initialize this repository with a README"
   - 点击 **"Create repository"**

4. **复制仓库地址**
   - 创建后会显示仓库地址，类似：
     - HTTPS: `https://github.com/你的用户名/仓库名.git`
     - SSH: `git@github.com:你的用户名/仓库名.git`

#### 步骤 2：连接本地仓库到 GitHub

在终端执行（替换为你的实际仓库地址）：

```bash
cd "/Users/ameng/Documents/projects/11.AI简历可行性评估"

# 添加远程仓库（使用HTTPS地址）
git remote add origin https://github.com/qiumeng0922/resume_extractor.git

# 或者使用SSH地址（如果你配置了SSH密钥）
# git remote add origin git@github.com:你的用户名/仓库名.git

# 推送代码到GitHub
git push -u origin master
```

如果遇到认证问题，GitHub 现在需要使用 Personal Access Token 而不是密码。

---

### 方法 2：使用 GitHub CLI（如果已安装）

```bash
# 安装 GitHub CLI（如果还没有）
# brew install gh

# 登录 GitHub
gh auth login

# 创建仓库并推送
cd "/Users/ameng/Documents/projects/11.AI简历可行性评估"
gh repo create AI简历可行性评估 --public --source=. --remote=origin --push
```

---

## 🔐 GitHub 认证设置

### 如果推送时要求输入密码

GitHub 不再支持密码认证，需要使用 **Personal Access Token**：

#### 创建 Personal Access Token：

1. **打开 GitHub 设置**
   - 访问：https://github.com/settings/tokens
   - 或：GitHub 头像 → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **生成新 Token**
   - 点击 **"Generate new token"** → **"Generate new token (classic)"**
   - **Note**: 填写描述，如 "AI简历项目"
   - **Expiration**: 选择过期时间（建议 90 天或更长）
   - **Select scopes**: 勾选 `repo`（完整仓库访问权限）
   - 点击 **"Generate token"**

3. **复制 Token**
   - ⚠️ **重要**：Token 只显示一次，立即复制保存！

4. **使用 Token 推送**
   ```bash
   git push -u origin master
   # 用户名：你的GitHub用户名
   # 密码：粘贴刚才复制的Token（不是GitHub密码）
   ```

---

## ✅ 验证设置

推送成功后，验证：

```bash
# 查看远程仓库
git remote -v

# 应该显示：
# origin  https://github.com/你的用户名/仓库名.git (fetch)
# origin  https://github.com/你的用户名/仓库名.git (push)
```

---

## 🎯 推送完成后

一旦代码推送到 GitHub，就可以：

1. **打开 GitHub 网页**
   - 访问你的仓库：`https://github.com/你的用户名/仓库名`

2. **进入 Actions 标签**
   - 点击仓库顶部的 **Actions** 标签

3. **运行工作流**
   - 找到 **"构建 Windows EXE"** 工作流
   - 点击 **"Run workflow"** 按钮
   - 等待构建完成
   - 下载生成的 exe 文件

---

## 🆘 常见问题

### 问题 1：推送被拒绝（403 Forbidden）

**原因**：认证失败

**解决**：
- 使用 Personal Access Token 而不是密码
- 检查 Token 是否有 `repo` 权限

### 问题 2：仓库已存在

**解决**：
```bash
# 如果远程仓库已存在，先删除再添加
git remote remove origin
git remote add origin https://github.com/你的用户名/仓库名.git
```

### 问题 3：分支名称不匹配

**解决**：
```bash
# 如果GitHub默认分支是main，而你的是master
git push -u origin master:main
# 或者重命名本地分支
git branch -M main
git push -u origin main
```

---

## 📝 快速命令总结

```bash
# 1. 添加远程仓库（替换为你的实际地址）
git remote add origin https://github.com/你的用户名/仓库名.git

# 2. 推送代码
git push -u origin master

# 3. 如果要求认证，使用Personal Access Token
```

---

**完成这些步骤后，就可以使用 GitHub Actions 自动打包 Windows EXE 了！** 🎉
