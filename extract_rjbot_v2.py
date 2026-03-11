#!/usr/bin/env python3
"""
RJ-BOT 网站内容提取和知识库构建脚本 v2
使用 agent-browser 逐步点击所有链接并提取内容
"""
import subprocess
import json
import os
import re
from datetime import datetime

class RJBOTKnowledgeBuilder:
    def __init__(self, output_dir="/root/.openclaw/workspace/rjbot-knowledge/docs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.visited_urls = set()
        
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
            
    def navigate_to_page(self, ref):
        """点击链接导航到页面"""
        stdout, stderr, code = self.run_agent_browser(f"click {ref}")
        if code != 0:
            print(f"❌ 点击失败: {stderr}")
            return False
            
        # 等待页面加载
        stdout, stderr, code = self.run_agent_browser("wait --load networkidle")
        return code == 0
        
    def get_current_page_info(self):
        """获取当前页面信息"""
        # 获取标题
        stdout, stderr, code = self.run_agent_browser("get title")
        title = stdout.strip() if code == 0 else "Unknown"
        
        # 获取 URL
        stdout, stderr, code = self.run_agent_browser("get url")
        url = stdout.strip() if code == 0 else "Unknown"
        
        # 获取内容
        stdout, stderr, code = self.run_agent_browser("get text body")
        content = stdout if code == 0 else ""
        
        return {
            'url': url,
            'title': title,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
    def save_to_obsidian(self, page_data, category):
        """保存到 Obsidian 格式"""
        if page_data['url'] in self.visited_urls:
            return None
            
        self.visited_urls.add(page_data['url'])
        
        # 创建安全的文件名
        safe_title = re.sub(r'[^\w\-_. ]', '', page_data['title']).strip()[:50]
        filename = f"{category}/{safe_title}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        # 创建分类目录
        category_dir = os.path.join(self.output_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # 写入内容
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {page_data['title']}\n\n")
            f.write(f"**URL:** {page_data['url']}\n")
            f.write(f"**Crawled At:** {page_data['timestamp']}\n")
            f.write(f"**Category:** {category}\n\n")
            f.write("---\n\n")
            f.write(page_data['content'])
            
        print(f"✅ 已保存: {filename}")
        return filepath
        
    def extract_all_from_homepage(self):
        """从主页提取所有链接的内容"""
        pages = []
        
        # 打开主页
        print("📄 打开主页...")
        stdout, stderr, code = self.run_agent_browser("open https://www.rj-bot.com/")
        if code != 0:
            print(f"❌ 打开主页失败: {stderr}")
            return pages
            
        self.run_agent_browser("wait --load networkidle")
        
        # 保存主页
        page_info = self.get_current_page_info()
        filepath = self.save_to_obsidian(page_info, 'Home')
        if filepath:
            pages.append({
                'url': page_info['url'],
                'category': 'Home',
                'filepath': filepath
            })
            
        # 点击所有主要链接
        main_links = [
            ('@e8', 'About'),      # ABOUT US
            ('@e51', 'News'),      # INDUSTRIES NEWS
            ('@e52', 'News'),      # COMPANY NEWS
            ('@e11', 'FAQ'),       # FAQ
            ('@e12', 'Contact'),   # CONTACT
            ('@e22', 'Products'),  # Fullset
            ('@e23', 'Products'),  # HVAC
            ('@e24', 'Products'),  # G36
            ('@e25', 'Products'),  # K20
            ('@e26', 'Products'),  # K22
            ('@e27', 'Products'),  # K18
            ('@e28', 'Products'),  # G31
            ('@e29', 'Products'),  # Q37
            ('@e45', 'Products'),  # Sewer Pipeline
            ('@e46', 'Products'),  # Grease Duct
            ('@e47', 'Products'),  # Air Duct
            ('@e48', 'Products'),  # Tank
            ('@e49', 'Products'),  # Livestock
            ('@e50', 'Products'),  # Accessories
        ]
        
        for ref, category in main_links:
            print(f"\n📄 访问链接 {ref} ({category})...")
            
            # 点击链接
            if not self.navigate_to_page(ref):
                continue
                
            # 获取页面信息
            page_info = self.get_current_page_info()
            
            # 检查是否是 404 页面
            if '404' in page_info['title'] or '404' in page_info['content']:
                print(f"⚠️  跳过 404 页面")
                continue
                
            # 保存页面
            filepath = self.save_to_obsidian(page_info, category)
            if filepath:
                pages.append({
                    'url': page_info['url'],
                    'category': category,
                    'filepath': filepath
                })
                
            # 返回主页
            self.run_agent_browser("open https://www.rj-bot.com/")
            self.run_agent_browser("wait --load networkidle")
            
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
    print("🚀 RJ-BOT 知识库构建工具 v2\n")
    
    builder = RJBOTKnowledgeBuilder()
    
    # 提取所有页面
    pages = builder.extract_all_from_homepage()
    
    # 创建索引
    builder.create_index(pages)
    
    print(f"\n✅ 完成！共爬取 {len(pages)} 个页面")
