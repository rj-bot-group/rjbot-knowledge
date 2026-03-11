#!/usr/bin/env python3
"""
RJ-BOT 产品详情页深度爬取脚本
从知识库中提取所有产品链接并爬取详情页
"""
import subprocess
import os
import re
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse

class ProductDetailCrawler:
    def __init__(self, base_url="https://www.rj-bot.com/", output_dir="/root/.openclaw/workspace/rjbot-knowledge/docs"):
        self.base_url = base_url
        self.output_dir = output_dir
        self.visited_urls = set()
        self.failed_urls = set()
        self.session_count = 0
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 定义所有产品详情页URL
        self.product_detail_urls = [
            # Q 系列风道清洗
            "https://www.rj-bot.com/product-details/q37-air-duct-clean-robot.html",
            "https://www.rj-bot.com/product-details/q50-air-duct-clean-robot.html",
            "https://www.rj-bot.com/product-details/q28-air-duct-clean-robot.html",
            "https://www.rj-bot.com/product-details/q30-air-duct-clean-shaft.html",
            "https://www.rj-bot.com/product-details/q29-air-duct-clean-Shaft.html",
            "https://www.rj-bot.com/product-details/q31-kitchen-duct-clean-robot.html",
            
            # G 系列油管道清洗
            "https://www.rj-bot.com/product-details/g36-grease-duct-clean-robot.html",
            
            # K 系列管道巡检
            "https://www.rj-bot.com/product-details/k22-pipeline-inspection-robot.html",
            "https://www.rj-bot.com/product-details/k22b-pipeline-inspection-robot.html",
            "https://www.rj-bot.com/product-details/K22-C-pipeline-inspection-robot.html",
            "https://www.rj-bot.com/product-details/k20-pipeline-inspection-robot.html",
            "https://www.rj-bot.com/product-details/k18-pipeline-inspection-robot.html",
            "https://www.rj-bot.com/product-details/q28-Inspection-robot.html",
            
            # 配套设备
            "https://www.rj-bot.com/product-details/p33-portable-high.html",
            "https://www.rj-bot.com/product-details/p40-high-pressure-suction.html",
            "https://www.rj-bot.com/product-details/w40-vacuum-cleaner.html",
            "https://www.rj-bot.com/product-details/w39-vacuum-cleaner.html",
            "https://www.rj-bot.com/product-details/p32-diesel-heater.html",
            "https://www.rj-bot.com/product-details/p24-chemical-spray-machine.html",
        ]
        
    def run_agent_browser(self, command):
        """运行 agent-browser 命令"""
        try:
            result = subprocess.run(
                f"agent-browser {command}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
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
        self.visited_urls = set()
        self.session_count += 1
        
    def get_page_info(self, url):
        """获取页面信息"""
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
        self.run_agent_browser("wait --load networkidle")
        
        # 获取标题
        stdout, stderr, code = self.run_agent_browser("get title")
        title = stdout.strip() if code == 0 else "Unknown"
        
        # 获取实际URL
        stdout, stderr, code = self.run_agent_browser("get url")
        actual_url = stdout.strip() if code == 0 else url
        
        # 检查是否是404
        if '404' in title or '404' in actual_url:
            print(f"  ⚠️  404页面，跳过")
            self.visited_urls.add(actual_url)
            return None
        
        # 获取内容
        stdout, stderr, code = self.run_agent_browser("get text body")
        content = stdout if code == 0 else ""
        
        # 检查空内容
        if not content.strip() or len(content.strip()) < 50:
            print(f"  ⚠️  内容为空，跳过")
            self.visited_urls.add(actual_url)
            return None
        
        return {
            'url': actual_url,
            'title': title,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
    def save_page(self, page_info):
        """保存页面到 Obsidian 格式"""
        if not page_info:
            return False
            
        self.visited_urls.add(page_info['url'])
        
        # 创建安全的文件名
        safe_title = re.sub(r'[^\w\-_. ]', '', page_info['title']).strip()[:60]
        filename = f"Products/{safe_title}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        # 创建目录
        category_dir = os.path.join(self.output_dir, "Products")
        os.makedirs(category_dir, exist_ok=True)
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {page_info['title']}\n\n")
            f.write(f"**URL:** {page_info['url']}\n")
            f.write(f"**Crawled At:** {page_info['timestamp']}\n")
            f.write(f"**Category:** Products\n\n")
            f.write("---\n\n")
            f.write(page_info['content'])
            
        print(f"  ✅ 已保存: {safe_title}")
        return True
        
    def crawl_all_product_details(self):
        """爬取所有产品详情页"""
        success_count = 0
        failed_count = 0
        
        print(f"=== 开始爬取 {len(self.product_detail_urls)} 个产品详情页 ===\n")
        
        for i, url in enumerate(self.product_detail_urls):
            # 每10个重启一次会话
            if i > 0 and i % 10 == 0:
                self.restart_session()
                
            # 打开主页确保会话状态
            if i % 5 == 0:
                self.run_agent_browser(f"open {self.base_url}")
                self.run_agent_browser("wait --load networkidle")
            
            page_info = self.get_page_info(url)
            if page_info:
                if self.save_page(page_info):
                    success_count += 1
            else:
                failed_count += 1
                
        return success_count, failed_count

if __name__ == "__main__":
    print("🚀 RJ-BOT 产品详情页爬取工具\n")
    
    crawler = ProductDetailCrawler()
    
    # 爬取所有产品详情页
    success, failed = crawler.crawl_all_product_details()
    
    print(f"\n✅ 完成！")
    print(f"  成功爬取: {success} 个页面")
    print(f"  失败/跳过: {failed} 个")
