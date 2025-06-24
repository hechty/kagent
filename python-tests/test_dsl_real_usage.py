#!/usr/bin/env python3
"""
通过实际使用DSL发现问题并修复
真实测试各种DSL功能的正确性
"""

import os
import requests
import json

# 禁用代理
for proxy_var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'all_proxy', 'ALL_PROXY']:
    os.environ.pop(proxy_var, None)

BASE_URL = "http://127.0.0.1:8080"

def test_basic_dsl_with_all_providers():
    """测试基础DSL调用各种提供商"""
    print("🔍 测试基础DSL调用各种提供商")
    print("="*50)
    
    providers_to_test = [
        ("DeepSeek", "deepseek"),
        ("OpenRouter", "openrouter")
    ]
    
    test_question = "请用一句话解释什么是人工智能？"
    
    for provider_name, provider_endpoint in providers_to_test:
        print(f"\n📡 测试 {provider_name} 提供商...")
        
        try:
            # 模拟DSL调用: "问题" using provider
            chat_data = {
                "messages": [{"role": "user", "content": test_question}],
                "model": "deepseek-chat" if provider_endpoint == "deepseek" else "google/gemini-2.0-flash-exp"
            }
            
            response = requests.post(f"{BASE_URL}/chat/{provider_endpoint}", json=chat_data, timeout=30)
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"   响应结构: {list(result.keys())}")
                    
                    # 检查choices字段
                    if "choices" in result:
                        if result["choices"] and len(result["choices"]) > 0:
                            answer = result["choices"][0]["message"]["content"]
                            print(f"   ✅ {provider_name} 成功: {answer[:50]}...")
                        else:
                            print(f"   ❌ {provider_name} choices为空: {result}")
                    else:
                        print(f"   ❌ {provider_name} 缺少choices字段: {result}")
                        
                except json.JSONDecodeError as e:
                    print(f"   ❌ {provider_name} JSON解析失败: {e}")
                    print(f"   响应内容: {response.text[:200]}")
            else:
                print(f"   ❌ {provider_name} HTTP错误: {response.status_code}")
                print(f"   错误内容: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ {provider_name} 异常: {e}")

def test_multiple_provider_comparison():
    """测试多提供商对比功能"""
    print("\n\n🔄 测试多提供商对比功能")
    print("="*50)
    
    try:
        # 模拟DSL的compare()功能
        comparison_data = {
            "question": "用一句话解释机器学习",
            "providers": ["deepseek", "openrouter"]
        }
        
        response = requests.post(f"{BASE_URL}/chat/multiple", json=comparison_data, timeout=60)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"响应结构: {list(result.keys())}")
                
                for provider, provider_result in result.items():
                    print(f"\n🤖 {provider} 结果:")
                    if isinstance(provider_result, dict):
                        if "choices" in provider_result:
                            if provider_result["choices"]:
                                answer = provider_result["choices"][0]["message"]["content"]
                                print(f"   ✅ 成功: {answer[:60]}...")
                            else:
                                print(f"   ❌ choices为空")
                        else:
                            print(f"   ❌ 缺少choices: {list(provider_result.keys())}")
                    else:
                        print(f"   ❌ 响应格式错误: {type(provider_result)}")
                        
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"响应内容: {response.text[:300]}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"错误内容: {response.text[:300]}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def test_provider_models():
    """测试提供商支持的模型"""
    print("\n\n📋 测试提供商支持的模型")
    print("="*50)
    
    try:
        response = requests.get(f"{BASE_URL}/models", timeout=15)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            models = response.json()
            print("支持的模型:")
            for provider, model_list in models.items():
                print(f"  {provider}: {model_list}")
        else:
            print(f"❌ 获取模型失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def test_different_models():
    """测试不同模型的调用"""
    print("\n\n🎯 测试不同模型的调用")
    print("="*50)
    
    model_tests = [
        ("DeepSeek Chat", "deepseek", "deepseek-chat"),
        ("DeepSeek Reasoner", "deepseek", "deepseek-reasoner"),
        ("Gemini Flash", "openrouter", "google/gemini-2.0-flash-exp"),
        ("GPT-4", "openrouter", "openai/gpt-4"),
    ]
    
    test_question = "什么是Kotlin语言的主要特点？"
    
    for model_name, provider, model_id in model_tests:
        print(f"\n🤖 测试 {model_name} ({model_id})...")
        
        try:
            chat_data = {
                "messages": [{"role": "user", "content": test_question}],
                "model": model_id
            }
            
            response = requests.post(f"{BASE_URL}/chat/{provider}", json=chat_data, timeout=45)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if "choices" in result and result["choices"]:
                        answer = result["choices"][0]["message"]["content"]
                        print(f"   ✅ {model_name} 成功: {answer[:80]}...")
                    else:
                        print(f"   ❌ {model_name} 响应格式问题: {result}")
                except:
                    print(f"   ❌ {model_name} 解析失败")
            else:
                print(f"   ❌ {model_name} HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ {model_name} 异常: {e}")

def diagnose_dsl_issues():
    """诊断DSL使用中的问题"""
    print("\n\n🔧 诊断DSL使用中的问题")
    print("="*50)
    
    issues_found = []
    
    # 问题1: 检查OpenRouter响应格式
    print("1. 检查OpenRouter响应格式...")
    try:
        chat_data = {
            "messages": [{"role": "user", "content": "测试"}],
            "model": "google/gemini-2.0-flash-exp"
        }
        response = requests.post(f"{BASE_URL}/chat/openrouter", json=chat_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   OpenRouter响应结构: {json.dumps(result, indent=2, ensure_ascii=False)[:300]}...")
            
            if "choices" not in result:
                issues_found.append("OpenRouter响应缺少choices字段")
            elif not result["choices"]:
                issues_found.append("OpenRouter响应choices为空数组")
        else:
            issues_found.append(f"OpenRouter HTTP错误: {response.status_code}")
            
    except Exception as e:
        issues_found.append(f"OpenRouter调用异常: {e}")
    
    # 问题2: 检查多提供商响应
    print("\n2. 检查多提供商对比响应...")
    try:
        comparison_data = {
            "question": "测试问题",
            "providers": ["deepseek"]  # 先只测试一个
        }
        response = requests.post(f"{BASE_URL}/chat/multiple", json=comparison_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   多提供商响应结构: {json.dumps(result, indent=2, ensure_ascii=False)[:300]}...")
        else:
            issues_found.append(f"多提供商对比HTTP错误: {response.status_code}")
            
    except Exception as e:
        issues_found.append(f"多提供商对比异常: {e}")
    
    # 总结问题
    print(f"\n📊 发现的问题总结:")
    if issues_found:
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
    else:
        print("   ✅ 未发现明显问题")
    
    return issues_found

def suggest_dsl_improvements():
    """基于发现的问题提出DSL改进建议"""
    print("\n\n💡 DSL改进建议")
    print("="*50)
    
    improvements = [
        {
            "问题": "API响应格式不一致",
            "现状": "不同提供商返回不同的响应结构",
            "建议": "在DSL层统一响应格式，隐藏Provider差异",
            "优先级": "高"
        },
        {
            "问题": "错误处理不完善",
            "现状": "DSL调用失败时缺少详细错误信息",
            "建议": "添加详细的错误处理和重试机制",
            "优先级": "高"
        },
        {
            "问题": "模型选择不够灵活",
            "现状": "需要手动指定model参数",
            "建议": "DSL支持智能模型选择：deepseek.chat(), deepseek.reasoner()",
            "优先级": "中"
        },
        {
            "问题": "缺少调试信息",
            "现状": "DSL调用失败时难以排查",
            "建议": "添加debug模式和详细日志",
            "优先级": "中"
        },
        {
            "问题": "性能监控缺失",
            "现状": "无法监控调用耗时和成功率",
            "建议": "内置性能监控和统计功能",
            "优先级": "低"
        }
    ]
    
    for improvement in improvements:
        print(f"\n🎯 {improvement['问题']}")
        print(f"   现状: {improvement['现状']}")
        print(f"   建议: {improvement['建议']}")
        print(f"   优先级: {improvement['优先级']}")

def main():
    """主测试流程"""
    print("🚀 开始DSL实际使用测试和问题诊断")
    print("="*70)
    
    # 1. 基础功能测试
    test_basic_dsl_with_all_providers()
    
    # 2. 多提供商对比测试
    test_multiple_provider_comparison()
    
    # 3. 模型列表测试
    test_provider_models()
    
    # 4. 不同模型测试
    test_different_models()
    
    # 5. 问题诊断
    issues = diagnose_dsl_issues()
    
    # 6. 改进建议
    suggest_dsl_improvements()
    
    print(f"\n🎉 DSL实际使用测试完成，发现 {len(issues)} 个问题需要修复")

if __name__ == "__main__":
    main()