#!/usr/bin/env python3
"""
测试MCP记忆服务器功能
"""

import json
import subprocess
import sys
import time
from pathlib import Path

def test_mcp_server():
    """测试MCP服务器功能"""
    print("🧪 测试MCP记忆服务器...")
    
    server_path = Path(__file__).parent / "memory-mcp-server.py"
    
    # 测试请求
    test_requests = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        },
        {
            "jsonrpc": "2.0", 
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "memory_status",
                "arguments": {}
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 3, 
            "method": "tools/call",
            "params": {
                "name": "memory_remember",
                "arguments": {
                    "content": "这是一个MCP测试记忆",
                    "title": "MCP测试",
                    "memory_type": "semantic",
                    "importance": 7.0,
                    "tags": ["测试", "MCP"]
                }
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call", 
            "params": {
                "name": "memory_recall",
                "arguments": {
                    "query": "MCP测试",
                    "max_results": 2
                }
            }
        }
    ]
    
    try:
        # 启动MCP服务器
        process = subprocess.Popen(
            [sys.executable, str(server_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✅ MCP服务器已启动")
        
        # 发送测试请求
        for i, request in enumerate(test_requests):
            print(f"\n📤 发送请求 {i+1}: {request['method']}")
            
            # 发送请求
            process.stdin.write(json.dumps(request) + "\n")
            process.stdin.flush()
            
            # 读取响应 (超时机制)
            try:
                # 简单的超时读取
                response_line = process.stdout.readline()
                if response_line:
                    response = json.loads(response_line.strip())
                    print(f"📥 响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
                else:
                    print("❌ 无响应")
            except Exception as e:
                print(f"❌ 响应解析失败: {e}")
        
        # 关闭进程
        process.terminate()
        process.wait(timeout=5)
        print("\n✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        if 'process' in locals():
            process.terminate()

def test_claude_mcp_integration():
    """测试Claude MCP集成"""
    print("\n🔧 测试Claude MCP集成...")
    
    try:
        # 检查Claude命令是否可用
        result = subprocess.run(["claude", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Claude Code可用: {result.stdout.strip()}")
        else:
            print("❌ Claude Code不可用")
            return False
        
        # 检查MCP命令
        result = subprocess.run(["claude", "mcp", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Claude MCP命令可用")
            print(f"当前MCP服务器:\n{result.stdout}")
        else:
            print("❌ Claude MCP命令失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Claude MCP集成测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 MCP记忆服务器完整测试")
    print("=" * 40)
    
    # 测试MCP服务器
    test_mcp_server()
    
    # 测试Claude集成
    test_claude_mcp_integration()