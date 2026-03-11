#!/usr/bin/env python3
"""
RJ-BOT 简化爬取脚本
直接访问关键页面，跳过404和空内容
"""
import subprocess
import os
import re
from datetime import datetime

class SimpleCrawler:
    def __init__(self, output_dir="/root/.openclaw/workspace/rjbot-knowledge/docs"):
        self.output_dir = output_dir
        self.visited_urls = set()
        os.makedirs(output_dir, exist_ok=True)
        
        # 定义要爬取的关键页面
        self.pages_to_crawl = [
            ("https://www.rj-bot.com/", "Home"),
            ("https://www.rj-bot.com/about.html", "About"),
            ("https://www.rj-bot.com/contact.html", "Contact"),
            ("https://www.rj-bot.com/service/faq.html", "FAQ"),
            ("https://www.rj-bot.com/news/company-news.html", "News"),
            ("https://www.rj-bot.com/news/industries-news.html", "News"),
            # 产品页面
            ("https://www.rj-bot.com/product/accessories.html", "Products"),
            ("https://www.rj-bot.com/product/air-duct-cleaning.html", "Products"),
            ("https://www.rj-bot.com/product-details/HVAC-Air-Vent-and-Duct-Cleaning-Solutions.html", "Products"),
            ("https://www.rj-bot.com/product-details/kitchen-clean-fullset.html", "Products"),
            ("https://www.rj-bot.com/product/grease-duct-cleaning.html", "Products"),
            ("https://www.rj-bot.com/product/sewer-pipeline-inspection.html", "Products"),
            ("https://www.rj-bot.com/product/tank-cleaning-solutions.html", "Products"),
            ("https://www.rj-bot.com/product/livestock-ditch-cleaning.html", "Products"),
        ]
        
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
            
    def crawl_page(self, url, category):
        """爬取单个页面"""
        if url in self.visited_urls:
            return False
            
        print(f"📄 {category}: {url}")
        
        # 打开页面
        stdout, stderr, code = self.run_agent_browser(f"open {url}")
        if code != 0:
            print(f"  ❌ 打开失败: {stderr}")
            return False
            
        # 等待加载
        self.run_agent_browser("wait --load networkidle")
        
        # 获取标题
        stdout, stderr, code = self.run_agent_browser("get title")
        title = stdout.strip() if code == 0 else "Unknown"
        
        # 获取URL
        stdout, stderr, code = self.run_agent_browser("get url")
        actual_url = stdout.strip() if code == 0 else url
        
        # 检查404
        if '404' in title or '404' in actual_url:
            print(f"  ⚠️  404页面，跳过")
            self.visited_urls.add(url)
            return False
        
        # 获取内容
        stdout, stderr, code = self.run_agent_browser("get text body")
        content = stdout if code == 0 else ""
        
        # 检查空内容
        if not content.strip() or len(content.strip()) < 50:
            print(f"  ⚠️  内容为空，跳过")
            self.visited_urls.add(url)
            return False
        
        # 保存页面
        return self.save_page(title, actual_url, content, category)
        
    def save_page(self, title, url, content, category):
        """保存页面"""
        self.visited_urls.add(url)
        
        # 安全文件名
        safe_title = re.sub(r'[^\w\-_. ]', '', title).strip()[:50]
        filename = f"{category}/{safe_title}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        # 创建分类目录
        category_dir = os.path.join(self.output_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(f"**URL:** {url}\n")
            f.write(f"**Crawled At:** {datetime.now().isoformat()}\n")
            f.write(f"**Category:** {category}\n\n")
            f.write("---\n\n")
            f.write(content)
            
        print(f"  ✅ 已保存: {safe_title}")
        return True
        
    def crawl_all(self):
        """爬取所有页面"""
        success_count = 0
        failed_count = 0
        
        for url, category in self.pages_to_crawl:
            if self.crawl_page(url, category):
                success_count += 1
            else:
                failed_count += 1
                
        return success_count, failed_count

if __name__ == "__main__":
    print("🚀 RJ-BOT 简化爬取工具\n")
    
    crawler = SimpleCrawler()
    
    # 爬取所有页面
    success, failed = crawler.crawl_all()
    
    print(f"\n✅ 完成！")
    print(f"  成功: {success} 个")
    print(f"  失败/跳过: {failed} 个")
