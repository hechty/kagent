#!/usr/bin/env python3
"""
基础聊天功能测试
测试LLM服务的聊天API基础功能（不需要真实API密钥）
"""

import requests
import json
import sys

def test_chat_invalid_provider():
    """测试无效的提供商"""
    try:
        payload = {
            "model": "gpt-4",
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }
        
        response = requests.post(
            "http://127.0.0.1:8080/chat/invalid_provider", 
            json=payload,
            timeout=5
        )
        
        print(f"无效提供商测试状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        # 应该返回错误
        response_data = response.json()
        assert "error" in response_data, "应该返回错误信息"
        assert "Invalid provider" in response_data["error"], "错误信息应该包含'Invalid provider'"
        
        print("✅ 无效提供商测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 无效提供商测试失败: {e}")
        return False

def test_chat_missing_body():
    """测试缺少请求体"""
    try:
        response = requests.post(
            "http://127.0.0.1:8080/chat/openai",
            timeout=5
        )
        
        print(f"缺少请求体测试状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        # 应该返回400错误或类似的客户端错误
        assert response.status_code >= 400, "应该返回客户端错误状态码"
        
        print("✅ 缺少请求体测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 缺少请求体测试失败: {e}")
        return False

def test_chat_invalid_json():
    """测试无效的JSON格式"""
    try:
        response = requests.post(
            "http://127.0.0.1:8080/chat/openai",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        print(f"无效JSON测试状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        # 应该返回400错误
        assert response.status_code >= 400, "应该返回客户端错误状态码"
        
        print("✅ 无效JSON测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 无效JSON测试失败: {e}")
        return False

def test_chat_provider_not_registered():
    """测试未注册的提供商（有效名称但未配置）"""
    try:
        payload = {
            "model": "gpt-4",
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }
        
        response = requests.post(
            "http://127.0.0.1:8080/chat/openai", 
            json=payload,
            timeout=5
        )
        
        print(f"未注册提供商测试状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        # 应该返回错误，因为提供商未注册
        response_data = response.json()
        assert "error" in response_data, "应该返回错误信息"
        
        print("✅ 未注册提供商测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 未注册提供商测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=== LLM服务基础聊天功能测试 ===")
    
    tests = [
        test_chat_invalid_provider,
        test_chat_missing_body,
        test_chat_invalid_json,
        test_chat_provider_not_registered
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"测试结果: {passed}/{len(tests)} 通过")
    
    if passed == len(tests):
        print("🎉 所有基础聊天功能测试通过！")
        sys.exit(0)
    else:
        print("💥 部分测试失败！")
        sys.exit(1)