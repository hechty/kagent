#!/usr/bin/env python3
"""
测试MCP服务器的具体功能
"""

import json
import subprocess
import threading
import time
import sys

def test_mcp_server():
    """测试MCP服务器功能"""
    print("🧪 测试MCP记忆服务器功能...")
    
    # 启动MCP服务器
    process = subprocess.Popen(
        ["/root/code/memory-mcp-server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    try:
        # 测试请求序列
        requests = [
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
            }
        ]
        
        print("✅ MCP服务器已启动")
        
        for i, request in enumerate(requests):
            print(f"\n📤 发送请求 {i+1}: {request['method']}")
            
            # 发送请求
            request_json = json.dumps(request) + "\n"
            process.stdin.write(request_json)
            process.stdin.flush()
            
            # 读取响应（设置超时）
            try:
                # 简单的超时机制
                def read_output():
                    try:
                        return process.stdout.readline()
                    except:
                        return None
                
                import threading
                result = [None]
                
                def target():
                    result[0] = read_output()
                
                thread = threading.Thread(target=target)
                thread.start()
                thread.join(timeout=5)
                
                if result[0]:
                    response_line = result[0].strip()
                    if response_line:
                        try:
                            response = json.loads(response_line)
                            print(f"📥 响应成功:")
                            if request['method'] == 'tools/list':
                                tools = response.get('result', {}).get('tools', [])
                                print(f"   发现 {len(tools)} 个工具:")
                                for tool in tools:
                                    print(f"   - {tool['name']}: {tool['description']}")
                            else:
                                print(f"   内容: {response}")
                        except json.JSONDecodeError as e:
                            print(f"❌ JSON解析失败: {e}")
                            print(f"   原始响应: {response_line}")
                    else:
                        print("❌ 收到空响应")
                else:
                    print("❌ 响应超时")
                    
            except Exception as e:
                print(f"❌ 读取响应失败: {e}")
        
        # 清理
        process.stdin.close()
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
        
        print("\n✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        process.terminate()

if __name__ == "__main__":
    test_mcp_server()