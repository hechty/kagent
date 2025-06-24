#!/usr/bin/env python3
"""
测试改进的DSL功能
验证我们的改进是否解决了发现的问题
"""

import os
import requests
import json
import time
from datetime import datetime

# 禁用代理
for proxy_var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'all_proxy', 'ALL_PROXY']:
    os.environ.pop(proxy_var, None)

BASE_URL = "http://127.0.0.1:8080"

def test_improved_dsl():
    """测试改进后的DSL功能"""
    print("🚀 测试改进后的DSL功能")
    print("=" * 60)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "summary": {}
    }
    
    # 1. 测试超时改进
    print("\n⏱️ 1. 测试超时配置改进")
    print("-" * 40)
    
    timeout_result = test_timeout_improvement()
    results["tests"]["timeout_improvement"] = timeout_result
    
    # 2. 测试错误处理改进  
    print("\n🛡️ 2. 测试错误处理改进")
    print("-" * 40)
    
    error_handling_result = test_error_handling_improvement()
    results["tests"]["error_handling"] = error_handling_result
    
    # 3. 测试复杂对话稳定性
    print("\n💬 3. 测试复杂对话稳定性")
    print("-" * 40)
    
    conversation_result = test_conversation_stability()
    results["tests"]["conversation_stability"] = conversation_result
    
    # 4. 测试批量请求
    print("\n📦 4. 测试批量请求处理")
    print("-" * 40)
    
    batch_result = test_batch_processing()
    results["tests"]["batch_processing"] = batch_result
    
    # 生成测试报告
    generate_test_report(results)
    
    return results

def test_timeout_improvement():
    """测试超时配置改进"""
    results = []
    
    # 测试简单请求（应该很快）
    try:
        start_time = time.time()
        response = make_chat_request("Just say 'OK'", timeout=10)
        end_time = time.time()
        
        if response and response.get("choices"):
            results.append({
                "test": "simple_request",
                "status": "success",
                "duration": round(end_time - start_time, 2),
                "response": response["choices"][0]["message"]["content"][:50]
            })
            print(f"✅ 简单请求: {end_time - start_time:.2f}秒")
        else:
            results.append({
                "test": "simple_request", 
                "status": "failed",
                "error": "No valid response"
            })
            print("❌ 简单请求失败")
            
    except Exception as e:
        results.append({
            "test": "simple_request",
            "status": "error", 
            "error": str(e)
        })
        print(f"❌ 简单请求异常: {e}")
    
    # 测试中等复杂请求
    try:
        start_time = time.time()
        response = make_chat_request(
            "Explain what a DSL is in programming in exactly 3 sentences.", 
            timeout=30
        )
        end_time = time.time()
        
        if response and response.get("choices"):
            results.append({
                "test": "medium_request",
                "status": "success", 
                "duration": round(end_time - start_time, 2),
                "response": response["choices"][0]["message"]["content"][:100]
            })
            print(f"✅ 中等请求: {end_time - start_time:.2f}秒")
        else:
            results.append({
                "test": "medium_request",
                "status": "failed",
                "error": "No valid response"
            })
            print("❌ 中等请求失败")
            
    except Exception as e:
        results.append({
            "test": "medium_request",
            "status": "error",
            "error": str(e)
        })
        print(f"❌ 中等请求异常: {e}")
    
    return results

def test_error_handling_improvement():
    """测试错误处理改进"""
    results = []
    
    # 测试无效提供商
    try:
        response = requests.post(f"{BASE_URL}/chat/invalid_provider", 
                               json={"messages": [{"role": "user", "content": "test"}]},
                               timeout=10)
        
        if response.status_code != 200:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            results.append({
                "test": "invalid_provider",
                "status": "expected_error",
                "error_type": error_data.get("error_type", "unknown"),
                "has_suggestion": "suggestion" in error_data,
                "has_available_providers": "available_providers" in error_data
            })
            print(f"✅ 无效提供商错误处理: {error_data.get('error_type', 'unknown')}")
            
            if "suggestion" in error_data:
                print(f"   📝 建议: {error_data['suggestion']}")
            if "available_providers" in error_data:
                print(f"   📋 可用提供商: {error_data['available_providers']}")
        else:
            results.append({
                "test": "invalid_provider",
                "status": "unexpected_success"
            })
            print("⚠️ 无效提供商竟然成功了")
            
    except Exception as e:
        results.append({
            "test": "invalid_provider",
            "status": "error",
            "error": str(e)
        })
        print(f"❌ 无效提供商测试异常: {e}")
    
    return results

def test_conversation_stability():
    """测试对话稳定性"""
    results = []
    
    conversation_messages = [
        {"role": "system", "content": "You are a helpful assistant. Keep responses brief."},
        {"role": "user", "content": "What is 1+1?"},
    ]
    
    try:
        # 第一轮对话
        response1 = make_chat_request_with_history(conversation_messages, timeout=30)
        
        if response1 and response1.get("choices"):
            answer1 = response1["choices"][0]["message"]["content"]
            conversation_messages.append({"role": "assistant", "content": answer1})
            conversation_messages.append({"role": "user", "content": "What about 2+2?"})
            
            # 第二轮对话
            response2 = make_chat_request_with_history(conversation_messages, timeout=30)
            
            if response2 and response2.get("choices"):
                answer2 = response2["choices"][0]["message"]["content"]
                
                results.append({
                    "test": "multi_turn_conversation",
                    "status": "success",
                    "turns": 2,
                    "responses": [answer1[:50], answer2[:50]]
                })
                print(f"✅ 多轮对话成功")
                print(f"   第1轮: {answer1[:50]}...")
                print(f"   第2轮: {answer2[:50]}...")
            else:
                results.append({
                    "test": "multi_turn_conversation",
                    "status": "failed_turn_2"
                })
                print("❌ 第二轮对话失败")
        else:
            results.append({
                "test": "multi_turn_conversation", 
                "status": "failed_turn_1"
            })
            print("❌ 第一轮对话失败")
            
    except Exception as e:
        results.append({
            "test": "multi_turn_conversation",
            "status": "error",
            "error": str(e)
        })
        print(f"❌ 对话测试异常: {e}")
    
    return results

def test_batch_processing():
    """测试批量请求处理"""
    results = []
    
    questions = [
        "What is AI?",
        "What is ML?", 
        "What is DL?"
    ]
    
    try:
        start_time = time.time()
        responses = []
        
        for i, question in enumerate(questions):
            print(f"   处理问题 {i+1}/3: {question}")
            response = make_chat_request(question, timeout=20)
            
            if response and response.get("choices"):
                responses.append({
                    "question": question,
                    "answer": response["choices"][0]["message"]["content"][:50],
                    "success": True
                })
            else:
                responses.append({
                    "question": question,
                    "success": False
                })
        
        end_time = time.time()
        success_count = sum(1 for r in responses if r["success"])
        
        results.append({
            "test": "batch_processing",
            "status": "completed",
            "total_questions": len(questions),
            "successful_responses": success_count,
            "total_duration": round(end_time - start_time, 2),
            "avg_duration": round((end_time - start_time) / len(questions), 2)
        })
        
        print(f"✅ 批量处理完成: {success_count}/{len(questions)} 成功")
        print(f"   总时间: {end_time - start_time:.2f}秒")
        print(f"   平均时间: {(end_time - start_time) / len(questions):.2f}秒/请求")
        
    except Exception as e:
        results.append({
            "test": "batch_processing",
            "status": "error", 
            "error": str(e)
        })
        print(f"❌ 批量处理异常: {e}")
    
    return results

def make_chat_request(message, timeout=30):
    """发送聊天请求"""
    chat_data = {
        "messages": [{"role": "user", "content": message}],
        "model": "google/gemini-2.5-pro"
    }
    
    response = requests.post(f"{BASE_URL}/chat/openrouter", json=chat_data, timeout=timeout)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"请求失败: {response.status_code} - {response.text[:200]}")
        return None

def make_chat_request_with_history(messages, timeout=30):
    """发送带历史的聊天请求"""
    chat_data = {
        "messages": messages,
        "model": "google/gemini-2.5-pro"
    }
    
    response = requests.post(f"{BASE_URL}/chat/openrouter", json=chat_data, timeout=timeout)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"请求失败: {response.status_code} - {response.text[:200]}")
        return None

def generate_test_report(results):
    """生成测试报告"""
    print("\n📊 DSL改进测试报告")
    print("=" * 60)
    
    total_tests = 0
    successful_tests = 0
    
    for test_category, test_results in results["tests"].items():
        print(f"\n📋 {test_category.replace('_', ' ').title()}:")
        
        for test_result in test_results:
            total_tests += 1
            test_name = test_result.get("test", "unknown")
            status = test_result.get("status", "unknown")
            
            if status in ["success", "expected_error", "completed"]:
                successful_tests += 1
                print(f"  ✅ {test_name}: {status}")
            else:
                print(f"  ❌ {test_name}: {status}")
                
            if "duration" in test_result:
                print(f"     ⏱️ 时间: {test_result['duration']}秒")
            if "error" in test_result:
                print(f"     ❌ 错误: {test_result['error']}")
    
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📈 总体结果:")
    print(f"   总测试数: {total_tests}")
    print(f"   成功数: {successful_tests}")
    print(f"   成功率: {success_rate:.1f}%")
    
    results["summary"] = {
        "total_tests": total_tests,
        "successful_tests": successful_tests,
        "success_rate": success_rate
    }
    
    # 保存详细报告
    with open("/root/code/dsl_improvement_test_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 详细报告已保存到: /root/code/dsl_improvement_test_report.json")

if __name__ == "__main__":
    test_improved_dsl()