#!/usr/bin/env python3
"""
RJ-BOT 网站深度爬取脚本
从主页开始，递归爬取所有页面
"""
import subprocess
import os
import re
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse

class DeepCrawler:
    def __init__(self, base_url="https://www.rj-bot.com/", output_dir="/root/.openclaw/workspace/rjbot-knowledge/docs"):
        self.base_url = base_url
        self.output_dir = output_dir
        self.visited_urls = set()
        self.queue = []
        self.max_pages = 50  # 最多爬取50个页面
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 添加主页到队列
        self.queue.append(base_url)
        
    def run_agent_browser(self, command):
        """运行 agent-browser 命令"""
        try:
            result = subprocess.run(
                f"agent-browser {command}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Timeout", 1
        except Exception as e:
            return "", str(e), 1
            
    def get_page_info(self, url):
        """获取页面信息"""
        print(f"📄 正在访问: {url}")
        
        # 打开页面
        stdout, stderr, code = self.run_agent_browser(f"open {url}")
        if code != 0:
            print(f"  ❌ 打开失败: {stderr}")
            return None
            
        # 等待页面加载
        self.run_agent_browser("wait --load networkidle")
        
        # 获取标题
        stdout, stderr, code = self.run_agent_browser("get title")
        title = stdout.strip() if code == 0 else "Unknown"
        
        # 获取 URL（可能有跳转）
        stdout, stderr, code = self.run_agent_browser("get url")
        actual_url = stdout.strip() if code == 0 else url
        
        # 检查是否是404页面
        if '404' in title or '404' in actual_url:
            print(f"  ⚠️  404页面，跳过")
            return None
        
        # 获取页面内容
        stdout, stderr, code = self.run_agent_browser("get text body")
        content = stdout if code == 0 else ""
        
        # 获取所有链接
        stdout, stderr, code = self.run_agent_browser("snapshot")
        links = self.extract_links(stdout)
        
        return {
            'url': actual_url,
            'title': title,
            'content': content,
            'links': links,
            'timestamp': datetime.now().isoformat()
        }
        
    def extract_links(self, snapshot_text):
        """从快照文本中提取链接"""
        links = []
        
        # 解析快照文本中的链接
        # 格式类似：- link "文本" [ref=eX]
        for line in snapshot_text.split('\n'):
            if 'link ' in line and '[ref=' in line:
                # 提取ref
                match = re.search(r'\[ref=(\w+)\]', line)
                if match:
                    ref = match.group(1)
                    links.append(ref)
                    
        return links
        
    def save_page(self, page_info):
        """保存页面到 Obsidian 格式"""
        if page_info['url'] in self.visited_urls:
            return False
            
        self.visited_urls.add(page_info['url'])
        
        # 确定分类
        category = self.determine_category(page_info['url'], page_info['title'])
        
        # 创建安全的文件名
        safe_title = re.sub(r'[^\w\-_. ]', '', page_info['title']).strip()[:50]
        filename = f"{category}/{safe_title}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        # 创建分类目录
        category_dir = os.path.join(self.output_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {page_info['title']}\n\n")
            f.write(f"**URL:** {page_info['url']}\n")
            f.write(f"**Crawled At:** {page_info['timestamp']}\n")
            f.write(f"**Category:** {category}\n\n")
            f.write("---\n\n")
            f.write(page_info['content'])
            
        print(f"  ✅ 已保存: {filename}")
        return True
        
    def determine_category(self, url, title):
        """根据 URL 和标题确定分类"""
        url_lower = url.lower()
        title_lower = title.lower()
        
        if 'about' in url_lower or 'about' in title_lower:
            return 'About'
        elif 'product' in url_lower or 'detail' in url_lower or 'equipment' in url_lower or 'robot' in title_lower:
            return 'Products'
        elif 'news' in url_lower or 'industr' in url_lower or 'company' in url_lower:
            return 'News'
        elif 'contact' in url_lower or 'email' in url_lower:
            return 'Contact'
        elif 'faq' in url_lower or 'service' in url_lower or 'download' in url_lower:
            return 'FAQ'
        else:
            return 'Other'
            
    def crawl(self):
        """执行深度爬取"""
        crawled_count = 0
        
        while self.queue and crawled_count < self.max_pages:
            url = self.queue.pop(0)
            
            if url in self.visited_urls:
                continue
                
            # 获取页面信息
            page_info = self.get_page_info(url)
            if not page_info:
                continue
                
            # 保存页面
            if self.save_page(page_info):
                crawled_count += 1
                
                # 添加新链接到队列
                for ref in page_info['links']:
                    # 点击链接获取实际 URL
                    stdout, stderr, code = self.run_agent_browser(f"click {ref}")
                    if code == 0:
                        self.run_agent_browser("wait --load networkidle")
                        stdout, stderr, code = self.run_agent_browser("get url")
                        new_url = stdout.strip() if code == 0 else None
                        
                        if new_url and new_url not in self.visited_urls:
                            # 只爬取同域名下的链接
                            if urlparse(new_url).netloc == urlparse(self.base_url).netloc:
                                self.queue.append(new_url)
                                
                        # 返回上一页
                        self.run_agent_browser(f"open {url}")
                        self.run_agent_browser("wait --load networkidle")
                        
        return crawled_count
        
    def create_index(self):
        """创建索引文件"""
        index_path = os.path.join(self.output_dir, "Index.md")
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("# RJ-BOT Knowledge Base Index\n\n")
            f.write(f"**Last Updated:** {datetime.now().isoformat()}\n")
            f.write(f"**Total Pages:** {len(self.visited_urls)}\n\n")
            f.write("---\n\n")
            
            # 按分类分组
            categories = {}
            for root, dirs, files in os.walk(self.output_dir):
                for file in files:
                    if file.endswith('.md') and file != 'Index.md':
                        category = os.path.basename(root)
                        if category == 'docs':
                            category = 'Home'
                            
                        if category not in categories:
                            categories[category] = []
                            
                        categories[category].append(os.path.join(root, file))
                        
            for category, files in sorted(categories.items()):
                f.write(f"## {category}\n\n")
                for filepath in sorted(files):
                    rel_path = os.path.relpath(filepath, self.output_dir)
                    filename = os.path.basename(filepath)
                    f.write(f"- [{filename}]({rel_path})\n")
                f.write("\n")
                
        print(f"✅ 索引已创建: {index_path}")

if __name__ == "__main__":
    print("🚀 RJ-BOT 深度爬取工具\n")
    
    crawler = DeepCrawler()
    
    # 执行爬取
    crawled = crawler.crawl()
    
    # 创建索引
    crawler.create_index()
    
    print(f"\n✅ 完成！共爬取 {crawled} 个页面")
