#!/usr/bin/env python3
"""
RJ-BOT 深度爬取脚本 v3
跳过 404 和空内容页面，深度爬取所有产品页
"""
import subprocess
import os
import re
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse
import hashlib

class DeepCrawlerV3:
    def __init__(self, base_url="https://www.rj-bot.com/", output_dir="/root/.openclaw/workspace/rjbot-knowledge/docs"):
        self.base_url = base_url
        self.output_dir = output_dir
        self.visited_urls = set()
        self.failed_urls = set()
        self.empty_pages = set()
        self.page_404 = set()
        self.max_pages = 100  # 最多爬取100个页面
        self.session_count = 0
        
        os.makedirs(output_dir, exist_ok=True)
        
    def run_agent_browser(self, command):
        """运行 agent-browser 命令"""
        try:
            result = subprocess.run(
                f"agent-browser {command}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=45
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Timeout", 1
        except Exception as e:
            return "", str(e), 1
            
    def restart_session(self):
        """重启浏览器会话"""
        print(f"🔄 重启浏览器会话 #{self.session_count}")
        stdout, stderr, code = self.run_agent_browser("close")
        
        # 重置访问记录
        self.visited_urls = set()
        self.session_count += 1
        
    def get_page_info(self, url):
        """获取页面信息"""
        # 检查是否已访问
        if url in self.visited_urls:
            return None
            
        print(f"📄 访问: {url}")
        
        # 打开页面
        stdout, stderr, code = self.run_agent_browser(f"open {url}")
        if code != 0:
            print(f"  ❌ 打开失败: {stderr}")
            self.failed_urls.add(url)
            return None
            
        # 等待页面加载
        stdout, stderr, code = self.run_agent_browser("wait --load networkidle")
        
        # 获取标题
        stdout, stderr, code = self.run_agent_browser("get title")
        title = stdout.strip() if code == 0 else "Unknown"
        
        # 获取实际URL（可能有重定向）
        stdout, stderr, code = self.run_agent_browser("get url")
        actual_url = stdout.strip() if code == 0 else url
        
        # 检查是否是404页面
        if '404' in title or '404' in actual_url:
            print(f"  ⚠️  404页面，跳过")
            self.page_404.add(actual_url)
            self.visited_urls.add(actual_url)
            return None
        
        # 获取页面内容
        stdout, stderr, code = self.run_agent_browser("get text body")
        content = stdout if code == 0 else ""
        
        # 检查内容是否为空
        if not content.strip() or len(content.strip()) < 50:
            print(f"  ⚠️  内容为空，跳过")
            self.empty_pages.add(actual_url)
            self.visited_urls.add(actual_url)
            return None
        
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
        
        for line in snapshot_text.split('\n'):
            if 'link ' in line and '[ref=' in line:
                match = re.search(r'\[ref=(\w+)\]', line)
                if match:
                    ref = match.group(1)
                    links.append(ref)
                    
        return links
        
    def save_page(self, page_info):
        """保存页面到 Obsidian 格式"""
        if not page_info:
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
            f.write(f"# { {page_info['title']}\n\n")
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
            
    def follow_link(self, ref, current_url):
        """点击链接并返回新页面URL"""
        # 点击链接
        stdout, stderr, code = self.run_agent_browser(f"click {ref}")
        if code != 0:
            print(f"  ❌ 点击失败: {stderr}")
            return None
            
        # 等待加载
        self.run_agent_browser("wait --load networkidle")
        
        # 获取新URL
        stdout, stderr, code = self.run_agent_browser("get url")
        new_url = stdout.strip() if code == 0 else None
        
        if new_url and new_url != current_url:
            # 只返回同域名下的链接
            if urlparse(new_url).netloc == urlparse(self.base_url).netloc:
                return new_url
                
        return None
        
    def crawl_from_homepage(self):
        """从主页深度爬取"""
        crawled_count = 0
        urls_to_visit = [self.base_url]
        product_urls = []
        
        print("=== 第一轮：从主页开始 ===")
        
        # 打开主页
        stdout, stderr, code = self.run_agent_browser(f"open {self.base_url}")
        if code != 0:
            print(f"❌ 打开主页失败: {stderr}")
            return 0
            
        self.run_agent_browser("wait --load networkidle")
        
        # 获取页面信息
        page_info = self.get_page_info(self.base_url)
        if page_info:
            if self.save_page(page_info):
                crawled_count += 1
                
                # 收集所有链接
                for ref in page_info['links']:
                    new_url = self.follow_link(ref, self.base_url)
                    if new_url:
                        # 优先产品页面
                        if 'product' in new_url.lower() or 'detail' in new_url.lower() or 'equipment' in new_url.lower():
                            if new_url not in product_urls:
                                product_urls.append(new_url)
                        urls_to_visit.append(new_url)
                        
                        # 返回主页
                        self.run_agent_browser(f"open {self.base_url}")
                        self.run_agent_browser("wait --load networkidle")
        
        print(f"\n=== 第二轮：爬取产品页 ===")
        print(f"产品页URL数: {len(product_urls)}")
        
        # 第二轮：重点爬取产品页
        for i, url in enumerate(product_urls[:50]):  # 最多50个产品页
            if i > 0 and i % 10 == 0:
                # 每爬取10个重启一次会话
                self.restart_session()
                
            page_info = self.get_page_info(url)
            if page_info:
                if self.save_page(page_info):
                    crawled_count += 1
                    
                    # 收集更多链接
                    for ref in page_info['links']:
                        new_url = self.follow_link(ref, url)
                        if new_url and new_url not in urls_to_visit:
                            urls_to_visit.append(new_url)
                            
                    # 返回主页
                    self.run_agent_browser(f"open {self.base_url}")
                    self.run_agent_browser("wait --load networkidle")
        
        return crawled_count
        
    def create_summary(self):
        """创建爬取汇总报告"""
        summary_path = os.path.join(self.output_dir, "..", "crawl_summary.txt")
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("RJ-BOT 知识库爬取汇总\n")
            f.write(f"爬取时间: {datetime.now().isoformat()}\n\n")
            f.write(f"成功爬取: {len(self.visited_urls)} 个页面\n")
            f.write(f"404页面: {len(self.page_404)} 个\n")
            f.write(f"空白页面: {len(self.empty_pages)} 个\n")
            f.write(f"失败页面: {len(self.failed_urls)} 个\n\n")
            f.write("=== 404页面列表 ===\n")
            for url in sorted(self.page_404):
                f.write(f"- {url}\n")
            f.write("\n=== 空白页面列表 ===\n")
            for url in sorted(self.empty_pages):
                f.write(f"- {url}\n")
                
        print(f"✅ 汇总已创建: {summary_path}")

if __name__ == "__main__":
    print("🚀 RJ-BOT 深度爬取工具 v3\n")
    
    crawler = DeepCrawlerV3()
    
    # 执行爬取
    crawled = crawler.crawl_from_homepage()
    
    # 创建汇总
    crawler.create_summary()
    
    print(f"\n✅ 完成！")
    print(f"  成功爬取: {crawled} 个页面")
    print(f"  跳过404: {len(crawler.page_404)} 个")
    print(f"  跳过空白: {len(crawler.empty_pages)} 个")
