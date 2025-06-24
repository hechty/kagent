#!/usr/bin/env python3
"""
健康检查测试
测试LLM服务的基础健康状态
"""

import requests
import sys
import os

# 禁用代理
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('all_proxy', None)
os.environ.pop('ALL_PROXY', None)

def test_health_check():
    """测试健康检查端点"""
    try:
        response = requests.get("http://127.0.0.1:8080/health", timeout=5)
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        assert response.status_code == 200, f"预期状态码200，实际得到{response.status_code}"
        assert response.text.strip() == "OK", f"预期响应'OK'，实际得到'{response.text.strip()}'"
        
        print("✅ 健康检查测试通过")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请确保服务正在运行")
        return False
    except AssertionError as e:
        print(f"❌ 测试失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        return False

def test_root_endpoint():
    """测试根端点"""
    try:
        response = requests.get("http://127.0.0.1:8080/", timeout=5)
        
        print(f"根端点状态码: {response.status_code}")
        print(f"根端点响应: {response.text}")
        
        assert response.status_code == 200, f"预期状态码200，实际得到{response.status_code}"
        
        print("✅ 根端点测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 根端点测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=== LLM服务健康检查测试 ===")
    
    health_ok = test_health_check()
    root_ok = test_root_endpoint()
    
    if health_ok and root_ok:
        print("\n🎉 所有健康检查测试通过！")
        sys.exit(0)
    else:
        print("\n💥 测试失败！")
        sys.exit(1)