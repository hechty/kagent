#!/usr/bin/env python3
"""
快速测试MCP服务器核心功能
"""

import json
import subprocess

def quick_test():
    """快速测试"""
    print("🚀 快速MCP测试")
    
    # 测试工具列表
    tools_request = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
    
    process = subprocess.Popen(
        ["/root/code/memory-mcp-server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    
    # 发送请求并关闭输入
    input_data = json.dumps(tools_request) + "\n"
    stdout, stderr = process.communicate(input=input_data, timeout=10)
    
    if stdout:
        lines = stdout.strip().split('\n')
        for line in lines:
            if line.strip():
                try:
                    response = json.loads(line)
                    if response.get('result', {}).get('tools'):
                        tools = response['result']['tools']
                        print(f"✅ 发现 {len(tools)} 个MCP工具:")
                        for tool in tools:
                            print(f"   • {tool['name']}")
                        return True
                except:
                    continue
    
    print("❌ MCP测试失败")
    return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n🎉 MCP服务器工作正常!")
        print("现在可以在Claude Code中使用记忆工具了!")
    else:
        print("\n⚠️ MCP服务器需要进一步调试")