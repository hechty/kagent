#!/usr/bin/env python3
"""
真实LLM功能测试
使用配置的真实API密钥测试实际的LLM对话功能
"""

import requests
import json
import sys
import time
import os

# 禁用代理
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('all_proxy', None)
os.environ.pop('ALL_PROXY', None)

def test_deepseek_chat():
    """测试DeepSeek聊天功能"""
    try:
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": "你好，请用一句话介绍自己"}
            ],
            "temperature": 0.7,
            "maxTokens": 100
        }
        
        print("测试DeepSeek聊天...")
        response = requests.post(
            "http://127.0.0.1:8080/chat/deepseek", 
            json=payload,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应ID: {result.get('id', 'N/A')}")
            if result.get('choices'):
                message = result['choices'][0]['message']['content']
                print(f"DeepSeek回复: {message}")
                
                # 验证响应结构
                assert 'id' in result, "响应应包含id字段"
                assert 'choices' in result, "响应应包含choices字段"
                assert len(result['choices']) > 0, "choices应该有至少一个元素"
                assert 'message' in result['choices'][0], "choice应该包含message"
                assert 'content' in result['choices'][0]['message'], "message应该包含content"
                
                print("✅ DeepSeek聊天测试通过")
                return True
            else:
                print("❌ 响应中没有choices")
                return False
        else:
            print(f"❌ DeepSeek请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ DeepSeek测试出错: {e}")
        return False

def test_openrouter_chat():
    """测试OpenRouter聊天功能"""
    try:
        payload = {
            "model": "openai/gpt-4.1",
            "messages": [
                {"role": "user", "content": "Hello, please introduce yourself in one sentence"}
            ],
            "temperature": 0.7,
            "maxTokens": 100
        }
        
        print("\n测试OpenRouter聊天...")
        response = requests.post(
            "http://127.0.0.1:8080/chat/openrouter", 
            json=payload,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应ID: {result.get('id', 'N/A')}")
            if result.get('choices'):
                message = result['choices'][0]['message']['content']
                print(f"OpenRouter回复: {message}")
                
                # 验证响应结构
                assert 'id' in result, "响应应包含id字段"
                assert 'choices' in result, "响应应包含choices字段"
                assert len(result['choices']) > 0, "choices应该有至少一个元素"
                
                print("✅ OpenRouter聊天测试通过")
                return True
            else:
                print("❌ 响应中没有choices")
                return False
        else:
            print(f"❌ OpenRouter请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ OpenRouter测试出错: {e}")
        return False

def test_multiple_providers():
    """测试多提供商并行聊天"""
    try:
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": "请简单回答：1+1等于几？"}
            ],
            "temperature": 0.3
        }
        
        print("\n测试多提供商并行聊天...")
        response = requests.post(
            "http://127.0.0.1:8080/chat/multiple", 
            json=payload,
            timeout=60
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            results = response.json()
            print("多提供商响应:")
            
            success_count = 0
            for provider, result in results.items():
                print(f"\n{provider}:")
                if isinstance(result, dict) and "error" in result:
                    print(f"  ❌ 错误: {result['error']}")
                elif isinstance(result, dict) and result.get('choices'):
                    message = result['choices'][0]['message']['content']
                    print(f"  ✅ 回复: {message}")
                    success_count += 1
                else:
                    print(f"  ⚠️ 意外响应格式: {type(result)} - {result}")
            
            print(f"\n成功响应数: {success_count}/{len(results)}")
            
            # 至少有一个成功就算通过
            if success_count > 0:
                print("✅ 多提供商聊天测试通过")
                return True
            else:
                print("❌ 所有提供商都失败了")
                return False
        else:
            print(f"❌ 多提供商请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 多提供商测试出错: {e}")
        return False

def test_models_list():
    """测试获取支持的模型列表"""
    try:
        print("\n测试模型列表...")
        response = requests.get("http://127.0.0.1:8080/models", timeout=10)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            models = response.json()
            print("支持的提供商和模型:")
            
            for provider, model_list in models.items():
                print(f"  {provider}: {model_list}")
            
            # 验证包含我们配置的提供商
            assert "DEEPSEEK" in models, "应该包含DEEPSEEK提供商"
            assert "OPENROUTER" in models, "应该包含OPENROUTER提供商"
            
            print("✅ 模型列表测试通过")
            return True
        else:
            print(f"❌ 模型列表请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 模型列表测试出错: {e}")
        return False

if __name__ == "__main__":
    print("=== LLM服务真实功能测试 ===")
    print("使用真实API密钥测试DeepSeek和OpenRouter")
    
    tests = [
        test_models_list,
        test_deepseek_chat,
        test_openrouter_chat,
        test_multiple_providers
    ]
    
    passed = 0
    for i, test in enumerate(tests):
        print(f"\n--- 测试 {i+1}/{len(tests)} ---")
        if test():
            passed += 1
        
        # 在测试之间稍作停顿，避免API限流
        if i < len(tests) - 1:
            time.sleep(2)
    
    print(f"\n{'='*50}")
    print(f"测试总结: {passed}/{len(tests)} 通过")
    
    if passed == len(tests):
        print("🎉 所有真实LLM功能测试通过！")
        sys.exit(0)
    else:
        print("💥 部分测试失败！")
        sys.exit(1)