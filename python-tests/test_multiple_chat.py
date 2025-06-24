#!/usr/bin/env python3
"""
多提供商聊天测试
测试LLM服务的多提供商并行聊天功能
"""

import requests
import json
import sys

def test_multiple_chat_endpoint():
    """测试多提供商聊天端点"""
    try:
        payload = {
            "model": "gpt-4",
            "messages": [
                {"role": "user", "content": "Hello, this is a test message"}
            ],
            "temperature": 0.7
        }
        
        response = requests.post(
            "http://127.0.0.1:8080/chat/multiple", 
            json=payload,
            timeout=10
        )
        
        print(f"多提供商聊天状态码: {response.status_code}")
        print(f"响应头 Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        # 解析响应
        response_data = response.json()
        print(f"响应数据类型: {type(response_data)}")
        
        if isinstance(response_data, dict):
            print("提供商响应结果:")
            for provider, result in response_data.items():
                print(f"  {provider}:")
                if isinstance(result, dict) and "error" in result:
                    print(f"    ❌ 错误: {result['error']}")
                else:
                    print(f"    ✅ 成功: {type(result)}")
        
        # 验证响应结构
        assert response.status_code == 200, f"预期状态码200，实际得到{response.status_code}"
        assert isinstance(response_data, dict), "响应应该是一个字典"
        
        # 检查是否包含预期的提供商
        expected_providers = ["OPENAI", "ANTHROPIC"]
        for provider in expected_providers:
            assert provider in response_data, f"响应中应该包含{provider}提供商"
            
            # 由于没有配置真实的API密钥，我们预期会有错误
            provider_result = response_data[provider]
            if isinstance(provider_result, dict) and "error" in provider_result:
                print(f"  {provider}: 预期的错误 - {provider_result['error']}")
            else:
                print(f"  {provider}: 意外的成功响应")
        
        print("✅ 多提供商聊天端点测试通过")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务")
        return False
    except json.JSONDecodeError:
        print(f"❌ 响应不是有效的JSON: {response.text}")
        return False
    except AssertionError as e:
        print(f"❌ 测试失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        return False

def test_multiple_chat_invalid_json():
    """测试多提供商聊天端点的错误处理"""
    try:
        response = requests.post(
            "http://127.0.0.1:8080/chat/multiple",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        print(f"无效JSON多提供商测试状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        # 应该返回400错误
        assert response.status_code >= 400, "应该返回客户端错误状态码"
        
        print("✅ 无效JSON多提供商测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 无效JSON多提供商测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=== LLM服务多提供商聊天测试 ===")
    
    tests = [
        test_multiple_chat_endpoint,
        test_multiple_chat_invalid_json
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"测试结果: {passed}/{len(tests)} 通过")
    
    if passed == len(tests):
        print("🎉 所有多提供商聊天测试通过！")
        sys.exit(0)
    else:
        print("💥 部分测试失败！")
        sys.exit(1)