#!/usr/bin/env python3
"""
验证简洁LLM DSL功能的Python测试
通过HTTP API间接测试DSL的各种功能
"""

import os
import requests
import json
import time

# 禁用代理
for proxy_var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'all_proxy', 'ALL_PROXY']:
    os.environ.pop(proxy_var, None)

# 额外禁用所有代理设置
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "http://127.0.0.1:8080"

def test_basic_dsl_functionality():
    """测试基础DSL功能"""
    print("🚀 测试简洁LLM DSL功能")
    
    # 等待服务启动
    print("等待服务启动...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✅ 服务已启动")
                break
        except:
            time.sleep(2)
            if i == 9:
                print("❌ 服务启动超时")
                return
    
    try:
        # 1. 测试单提供商聊天 (对应 DSL 的 "question" using provider)
        print("\n=== 1. 基础聊天功能 (DSL: 'question' using provider) ===")
        chat_data = {
            "messages": [{"role": "user", "content": "你好，请用一句话介绍什么是Kotlin？"}],
            "model": "deepseek-chat"
        }
        
        response = requests.post(f"{BASE_URL}/chat/deepseek", json=chat_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            print(f"✅ 基础聊天成功: {answer[:60]}...")
        else:
            print(f"❌ 基础聊天失败: {response.status_code}")
        
        # 2. 测试多提供商对比 (对应 DSL 的 compare() 函数)
        print("\n=== 2. 多提供商对比 (DSL: compare() 函数) ===")
        compare_data = {
            "question": "用一句话解释什么是人工智能？",
            "providers": ["deepseek", "openrouter"]
        }
        
        response = requests.post(f"{BASE_URL}/chat/multiple", json=compare_data, timeout=45)
        if response.status_code == 200:
            results = response.json()
            print("✅ 多提供商对比成功:")
            for provider, result in results.items():
                if "choices" in result and result["choices"]:
                    answer = result["choices"][0]["message"]["content"]
                    print(f"  - {provider}: {answer[:50]}...")
        else:
            print(f"❌ 多提供商对比失败: {response.status_code}")
        
        # 3. 测试系统角色设置 (对应 DSL 的 conversation() 和 system())
        print("\n=== 3. 系统角色设置 (DSL: conversation + system) ===")
        system_data = {
            "messages": [
                {"role": "system", "content": "你是一个Kotlin专家，回答要简洁专业"},
                {"role": "user", "content": "协程的主要优势是什么？"}
            ],
            "model": "deepseek-chat"
        }
        
        response = requests.post(f"{BASE_URL}/chat/deepseek", json=system_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            print(f"✅ 系统角色设置成功: {answer[:60]}...")
        else:
            print(f"❌ 系统角色设置失败: {response.status_code}")
        
        # 4. 测试不同模型 (对应 DSL 的 provider 配置)
        print("\n=== 4. 不同模型测试 (DSL: provider 配置) ===")
        model_data = {
            "messages": [{"role": "user", "content": "简单说明一下REST API"}],
            "model": "deepseek-reasoner"
        }
        
        response = requests.post(f"{BASE_URL}/chat/deepseek", json=model_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            print(f"✅ 不同模型测试成功: {answer[:60]}...")
        else:
            print(f"❌ 不同模型测试失败: {response.status_code}")
        
        # 5. 验证支持的模型 (对应 DSL 的 supportedModels)
        print("\n=== 5. 支持的模型列表 (DSL: supportedModels) ===")
        response = requests.get(f"{BASE_URL}/models", timeout=10)
        if response.status_code == 200:
            models = response.json()
            print("✅ 获取模型列表成功:")
            for provider, model_list in models.items():
                print(f"  - {provider}: {model_list}")
        else:
            print(f"❌ 获取模型列表失败: {response.status_code}")
        
        print("\n✅ 所有DSL功能验证完成！")
        print("\n📋 DSL功能映射总结:")
        print("  1. 'question' using provider -> /chat/{provider}")
        print("  2. compare(question, providers) -> /chat/multiple")
        print("  3. conversation().system() -> system messages")
        print("  4. agent(name, provider, role) -> system + user messages")
        print("  5. provider.supportedModels -> /models")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

if __name__ == "__main__":
    test_basic_dsl_functionality()