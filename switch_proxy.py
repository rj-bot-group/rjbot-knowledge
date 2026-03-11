#!/usr/bin/env python3
import subprocess
import json

def switch_proxy_group(group_name, node_name):
    """切换 Clash Meta 代理组"""
    try:
        result = subprocess.run(
            f"curl -s -X PUT http://127.0.0.1:9090/proxies/{group_name}?name={node_name}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def get_proxy_status():
    """获取代理状态"""
    try:
        result = subprocess.run(
            "curl -s http://127.0.0.1:9090/proxies",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

if __name__ == "__main__":
    print("=== 获取代理状态 ===")
    stdout, stderr, code = get_proxy_status()
    if code == 0:
        data = json.loads(stdout)
        proxies = data.get('proxies', {})
        
        print(f"📊 当前代理组：")
        for name, group in proxies.items():
            if 'type' in group:
                group_type = group['type']
                now = group.get('now', 'N/A')
                print(f"  [{group_type}] {name}: {now}")
                
                # 查找香港节点
                if group_type in ['select', 'Selector'] and 'all' in group:
                    for node in group['all']:
                        if '香港' in node:
                            alive = '✅' if node in proxies and proxies[node].get('alive', False) else '❓'
                            print(f"    {alive} {node}")
                            # 切换到这个节点
                            print(f"\n=== 切换到香港节点 ===")
                            switch_result = switch_proxy_group(name, node)
                            print(f"切换结果: {switch_result}")
                            break
                    break
        print()
        
        # 切换后状态
        stdout, stderr, code = get_proxy_status()
        if code == 0:
            data = json.loads(stdout)
            proxies = data.get('proxies', {})
            
            for name, group in proxies.items():
                if 'type' in group:
                    now = group.get('now', 'N/A')
                    if name != 'GLOBAL' and name != '🚀 节点选择':
                        print(f"{name}: {now}")
    else:
        print(f"❌ 获取状态失败: {stderr}")
