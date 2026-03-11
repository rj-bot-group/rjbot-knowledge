#!/usr/bin/env python3
"""
RJ-BOT 网站内容提取和知识库构建脚本
"""
import subprocess
import json
import os
from datetime import datetime

class RJBOTKnowledgeBuilder:
    def __init__(self, output_dir="/root/.openclaw/workspace/rjbot-knowledge/docs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
       
        
        # 设置代理环境
        os.environ['http_proxy'] = 'http://127.0.0.1:7890'
        os.environ['https_proxy'] = 'http://127.0.0.1:7890'
        
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
            
    def get_page_content(self, url):
        """获取网页完整内容"""
        print(f"📄 正在访问: {url}")
        
        # 打开页面
        stdout, stderr, code = self.run_agent_browser(f"open {url}")
        if code != 0:
            print(f"❌ 打开页面失败: {stderr}")
            return None
            
        # 等待页面加载
        stdout, stderr, code = self.run_agent_browser("wait --load networkidle")
        if code != 0:
            print(f"❌ 等待加载失败: {stderr}")
            
        # 获取页面标题
        stdout, stderr, code = self.run_agent_browser("get title")
        title = stdout.strip() if code == 0 else "Unknown"
        
        # 获取页面文本内容
        stdout, stderr, code = self.run_agent_browser("get text body")
        content = stdout if code == 0 else ""
        
        # 获取当前 URL
        stdout, stderr, code = self.run_agent_browser("get url")
        current_url = stdout.strip() if code == 0 else url
        
        return {
            'url': current_url,
            'title': title,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
    def save_to_obsidian(self, page_data, category):
        """保存到 Obsidian 格式"""
        # 创建安全的文件名
        safe_title = page_data['title'].replace('/', '-').replace('\\', '-')[:50]
        filename = f"{category}/{safe_title}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        # 创建分类目录
        category_dir = os.path.join(self.output_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # 写入 Obsidian 格式的内容
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {page_data['title']}\n\n")
            f.write(f"**URL:** {page_data['url']}\n")
            f.write(f"**Crawled At:** {page_data['timestamp']}\n")
            f.write(f"**Category:** {category}\n\n")
            f.write("---\n\n")
            f.write(page_data['content'])
            
        print(f"✅ 已保存: {filename}")
        return filepath
        
    def extract_all(self):
        """提取所有页面"""
        pages = []
        
        # 定义要访问的页面
        page_list = [
            ('https://www.rj-bot.com/', 'Home'),
            ('https://www.rj-bot.com/about', 'About'),
            ('https://www.rj-bot.com/products', 'Products'),
            ('https://www.rj-bot.com/news', 'News'),
            ('https://www.rj-bot.com/faq', 'FAQ'),
            ('https://www.rj-bot.com/contact', 'Contact'),
            
            # 产品页面
            ('https://www.rj-bot.com/products/fullset', 'Products'),
            ('https://www.rj-bot.com/products/hvac', 'Products'),
            ('https://www.rj-bot.com/products/g36', 'Products'),
            ('https://www.rj-bot.com/products/k20', 'Products'),
            ('https://www.rj-bot.com/products/k22', 'Products'),
            ('https://www.rj-bot.com/products/k18', 'Products'),
            ('https://www.rj-bot.com/products/g31', 'Products'),
            ('https://www.rj-bot.com/products/q37', 'Products'),
        ]
        
        for url, category in page_list:
            page_data = self.get_page_content(url)
            if page_data:
                filepath = self.save_to_obsidian(page_data, category)
                pages.append({
                    'url': url,
                    'category': category,
                    'filepath': filepath
                })
                
        return pages
        
    def create_index(self, pages):
        """创建索引文件"""
        index_path = os.path.join(self.output_dir, "Index.md")
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("# RJ-BOT Knowledge Base Index\n\n")
            f.write(f"**Last Updated:** {datetime.now().isoformat()}\n")
            f.write(f"**Total Pages:** {len(pages)}\n\n")
            f.write("---\n\n")
            
            # 按分类分组
            categories = {}
            for page in pages:
                if page['category'] not in categories:
                    categories[page['category']] = []
                categories[page['category']].append(page)
                
            for category, items in sorted(categories.items()):
                f.write(f"## {category}\n\n")
                for item in items:
                    f.write(f"- [{os.path.basename(item['filepath'])}]({item['filepath']})\n")
                f.write("\n")
                
        print(f"✅ 索引已创建: {index_path}")
        return index_path

if __name__ == "__main__":
    print("🚀 RJ-BOT 知识库构建工具\n")
    
    builder = RJBOTKnowledgeBuilder()
    
    # 提取所有页面
    pages = builder.extract_all()
    
    # 创建索引
    builder.create_index(pages)
    
    print(f"\n✅ 完成！共爬取 {len(pages)} 个页面")
