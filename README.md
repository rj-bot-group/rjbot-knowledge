# RJ-BOT 知识库项目

## 项目简介
这是从 RJ-BOT 官网（https://www.rj-bot.com/））爬取并整理的知识库，包含公司介绍、产品信息、解决方案等内容。

## 知识库结构

```
docs/
├── Index.md                     # 知识库索引
├── About/                      # 关于我们（2 个文档）
├── Contact/                    # 联系我们（2 个文档）
├── FAQ/                         # 常见问题（2 个文档）
├── Home/                        # 主页（1 个文档）
├── News/                        # 新闻动态（3 个文档）
└── Products/                    # 产品中心（10 个文档）
```

## 统计信息

| 类别 | 文档数 |
|------|--------|
| About | 2 |
| Contact | 2 |
| FAQ | 2 |
| Home | 1 |
| News | 3 |
| Products | 10 |
| **总计** | **21** |

## 文档格式
所有文档使用 Obsidian Markdown 格式，包含：
- 页面标题
- 源 URL
- 爬取时间
- 分类内容

## GitHub 仓库

- **仓库地址：** https://github.com/rj-bot-group/rjbot-knowledge
- **最后更新：** 2026-03-11
- **提交次数：** 3 次提交

## 使用方法

### 查看知识库
```bash
# 克隆仓库
git clone https://github.com/rj-bot-group/rjbot-knowledge.git

# 导入到 Obsidian
# 将克隆的文件夹添加为 Obsidian Vault
```

### 更新知识库
```bash
cd rjbot-knowledge
python3 deep_crawler.py  # 重新爬取
git add .
git commit -m "Update: Refreshed content"
git push
```

## 许可证
此知识库仅供 RJ-BOT 内部使用。
