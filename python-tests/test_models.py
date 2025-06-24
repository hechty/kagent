#!/usr/bin/env python3
"""
模型列表测试
测试LLM服务的支持模型查询功能
"""

import requests
import json
import sys

def test_models_endpoint():
    """测试获取支持模型的端点"""
    try:
        response = requests.get("http://127.0.0.1:8080/models", timeout=5)
        
        print(f"模型端点状态码: {response.status_code}")
        print(f"响应头 Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        assert response.status_code == 200, f"预期状态码200，实际得到{response.status_code}"
        
        # 尝试解析JSON响应
        try:
            models_data = response.json()
            print(f"支持的模型提供商: {list(models_data.keys())}")
            
            # 打印每个提供商的模型
            for provider, models in models_data.items():
                print(f"\n{provider} 支持的模型:")
                for model in models:
                    print(f"  - {model}")
            
            # 验证响应结构
            assert isinstance(models_data, dict), "响应应该是一个字典"
            
            # 检查是否包含一些预期的提供商
            expected_providers = ["OPENAI", "ANTHROPIC", "BAIDU", "ALIBABA"]
            for provider in expected_providers:
                if provider in models_data:
                    print(f"✅ 找到提供商: {provider}")
                    assert isinstance(models_data[provider], list), f"{provider}的模型列表应该是数组"
                    assert len(models_data[provider]) > 0, f"{provider}应该至少有一个模型"
                else:
                    print(f"⚠️ 未找到提供商: {provider} (可能未配置)")
            
            print("✅ 模型端点测试通过")
            return True
            
        except json.JSONDecodeError:
            print(f"❌ 响应不是有效的JSON: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务")
        return False
    except AssertionError as e:
        print(f"❌ 测试失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        return False

if __name__ == "__main__":
    print("=== LLM服务模型列表测试 ===")
    
    if test_models_endpoint():
        print("\n🎉 模型列表测试通过！")
        sys.exit(0)
    else:
        print("\n💥 模型列表测试失败！")
        sys.exit(1)