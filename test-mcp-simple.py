#!/usr/bin/env python3
"""
简单测试MCP记忆服务器
"""

import json
import subprocess
import sys
import time
from pathlib import Path

def test_mcp_server_basic():
    """基础MCP服务器测试"""
    print("🧪 测试MCP记忆服务器基础功能...")
    
    server_path = Path(__file__).parent / "memory-mcp-server.py"
    
    # 测试工具列表请求
    tools_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
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
        
        # 发送工具列表请求
        input_data = json.dumps(tools_request) + "\n"
        process.stdin.write(input_data)
        process.stdin.flush()
        
        # 等待响应
        try:
            process.stdin.close()
            stdout, stderr = process.communicate(timeout=10)
            
            if stdout:
                print("📥 服务器响应:")
                print(stdout)
            
            if stderr:
                print("⚠️ 错误输出:")
                print(stderr)
                
        except subprocess.TimeoutExpired:
            print("⏰ 响应超时")
            process.terminate()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_mcp_server_basic()