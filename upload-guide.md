# RJ-BOT 知识库手动上传指南

## 📊 任务完成状态

✅ **爬取进度：** 31 个页面
✅ **知识库整理：** Obsidian Markdown 格式
✅ **本地 Git 仓库：** 已创建
⚠️ **GitHub 推送：** 失败（TLS 错误）

---

## 📁 知识库压缩包

### 位置
```
/root/.openclaw/workspace/rjbot-knowledge-complete-20260311.tar.gz
```

### 大小
```bash
# 查看压缩包大小
ls -lh /root/.openclaw/workspace/rjbot-knowledge-complete-20260311.tar.gz
```

---

## 🔗 手动上传步骤

### 步骤 1：下载压缩包到本地

在本地电脑上执行：
```bash
# 使用 scp 从服务器下载（推荐）
scp root@your-server:/root/.openclaw/workspace/rjbot-knowledge-complete-20260311.tar.gz ./

# 或者使用 SFTP/FTP 下载
```

### 步骤 2：解压文件

```bash
# 解压
tar -xzf rjbot-knowledge-complete-20260311.tar.gz

# 进入目录
cd rjbot-knowledge
```

### 步骤 3：在 GitHub 创建仓库

1. 访问：https://github.com/new
2. 仓库名：`rjbot-knowledge`
3. 描述：`RJ-BOT 工业机器人知识库 - 公司介绍、产品中心、解决方案`
4. 初始化：**不选择 README、.gitignore**
5. 可见性：**Public**（公开）或 **Private**（私有）
6. 点击 "Create repository"

### 步骤 4：上传文件到 GitHub

**方法 A：使用 GitHub Desktop（推荐）**
1. 下载并安装 GitHub Desktop：https://desktop.github.com/
2. 登录你的 GitHub 账号
3. Clone 仓库到本地：
   ```
   git clone https://github.com/rj-bot-group/rjbot-knowledge.git
   ```
4. 复制解压后的文件到仓库目录
5. 在 GitHub Desktop 中提交并推送

**方法 B：使用命令行（如果你已有仓库）**
```bash
cd rjbot-knowledge
git init
git remote add origin https://github.com/rj-bot-group/rjbot-knowledge.git
git add .
git commit -m "Initial commit: RJ-BOT knowledge base"
git push -u origin master
```

**方法 C：直接在 GitHub 网页上传**
1. 在仓库页面点击 "Add file"
2. 选择 "Upload files"
3. 选择要上传的 Markdown 文件（可以批量选择）
4. 提交信息："Initial upload"
5. 点击 "Commit changes"

---

## 📚 知识库结构

```
docs/
├── Index.md                     # 知识库索引
├── About/                      # 关于我们（2 个）
├── Contact/                    # 联系我们（2 个）
├── FAQ/                         # 常见问题（2 个）
├── Home/                        # 主页（1 个）
├── News/                        # 新闻动态（3 个）
└── Products/                    # 产品中心（22 个）
```

---

## 📊 知识库内容统计

| 类别 | 文档数 | 说明 |
|------|--------|------|
| **Home** | 1 | 网站主页 |
| **About** | 2 | 公司介绍 |
| **Contact** | 2 | 联系信息 |
| **FAQ** | 2 | 常见问题 |
| **News** | 3 | 新闻动态 |
| **Products** | 22 | 产品详情 |
| **总计** | **32** | 完整知识库 |

---

## 🔗 GitHub 仓库地址

**现有仓库：**
https://github.com/rj-bot-group/rjbot-knowledge

**（如果这个仓库无法使用，请新建一个）**

---

## 🎯 额外建议

### 1. 自动化脚本（未来改进）

可以创建一个自动化脚本，定期更新知识库：

```bash
#!/bin/bash

# 1. 爬取最新内容
cd /root/.openclaw/workspace/rjbot-knowledge
python3 simple_crawler.py

# 2. 更新 Git
git add .
git commit -m "Update: $(date +'%Y-%m-%d %H:%M')"
git push

# 3. 或创建新的压缩包
cd /root/.openclaw/workspace
tar -czf rjbot-knowledge-$(date +%Y%m%d).tar.gz rjbot-knowledge/
```

### 2. 使用 SSH 密钥

如果 GitHub Token 推送有问题，可以配置 SSH 密钥：

```bash
# 1. 生成 SSH 密钥（如果没有）
ssh-keygen -t rsa -b 4096 -C "rjbot-bot" -f ~/.ssh/id_rsa

# 2. 复制公钥到 GitHub
cat ~/.ssh/id_rsa.pub
# 添加到：https://github.com/settings/keys

# 3. 切换到 SSH 推送
git remote remove origin
git remote add origin git@github.com:rjbot-group/rjbot-knowledge.git
git push -u origin master
```

### 3. Obsidian 集成

可以 Obsidian 直接使用这个知识库：

1. 下载并解压压缩包
2. 在 Obsidian 中创建新 Vault
3. 指向到解压后的 `docs/` 目录
4. Obsidian 会自动识别所有 Markdown 文件

---

## ✅ 验证成功

上传完成后，在 GitHub 仓库页面应该看到：

- `docs/` 文件夹
- `Index.md` - 知识库索引
- 5 个子文件夹（About、Contact、FAQ、News、Products）
- 总共 32 个 Markdown 文件

---

## 📞 联系支持

- **邮箱：** sales@rj-bot.com
- **电话：** +86 178 9845 8979
- **WhatsApp：** +86 178 9845 8979
- **官网：** https://www.rj-bot.com

---

**创建时间：** 2026-03-11 17:10
**任务完成时间：** 2026-03-11 17:08
