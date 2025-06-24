#!/usr/bin/env python3
"""
修复DSL问题后的正确使用方式
使用正确的模型名称和API调用方式
"""

import os
import requests
import json
import time

# 禁用代理
for proxy_var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'all_proxy', 'ALL_PROXY']:
    os.environ.pop(proxy_var, None)

BASE_URL = "http://127.0.0.1:8080"

def use_dsl_correctly():
    """正确使用DSL调用各种模型"""
    print("🔧 使用修复后的DSL正确调用模型")
    print("="*60)
    
    # 1. 使用正确的DeepSeek调用
    print("\n1. 测试DeepSeek Chat...")
    try:
        chat_data = {
            "messages": [{"role": "user", "content": "请用一句话解释什么是DSL？"}],
            "model": "deepseek-chat"
        }
        
        response = requests.post(f"{BASE_URL}/chat/deepseek", json=chat_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and result["choices"]:
                answer = result["choices"][0]["message"]["content"]
                print(f"   ✅ DeepSeek成功: {answer}")
            else:
                print(f"   ❌ DeepSeek格式问题: {result}")
        else:
            print(f"   ❌ DeepSeek HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ DeepSeek异常: {e}")
    
    # 2. 使用正确的Gemini模型名称
    print("\n2. 测试Gemini 2.5 Pro (正确模型名)...")
    try:
        chat_data = {
            "messages": [{"role": "user", "content": "请评估Kotlin DSL的设计优劣？"}],
            "model": "google/gemini-2.5-pro"  # 使用正确的模型名
        }
        
        response = requests.post(f"{BASE_URL}/chat/openrouter", json=chat_data, timeout=45)
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and result["choices"]:
                answer = result["choices"][0]["message"]["content"]
                print(f"   ✅ Gemini成功: {answer[:100]}...")
                return answer  # 返回Gemini的回答用于进一步讨论
            else:
                print(f"   ❌ Gemini格式问题: {result}")
        else:
            print(f"   ❌ Gemini HTTP错误: {response.status_code}")
            print(f"   错误内容: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Gemini异常: {e}")
    
    return None

def discuss_dsl_improvements_with_gemini():
    """使用DSL与Gemini讨论DSL改进方案"""
    print("\n\n🤖 使用DSL与Gemini讨论DSL改进")
    print("="*60)
    
    try:
        # 第一轮：让Gemini分析当前DSL
        analysis_prompt = """
作为AI架构专家，请分析这个Kotlin LLM DSL的设计：

当前DSL功能:
1. 基础调用: "问题" using deepseek("key")
2. 对话管理: SimpleConversation, system(), ask()  
3. Agent系统: agent(name, provider, role).solve()
4. 多模型对比: compare(question, providers)
5. 批量处理: processAll(), 回退策略: withFallback()

实际使用中发现的问题:
1. OpenRouter模型名称不一致 (gemini-2.0-flash-exp vs gemini-2.5-pro)
2. 错误处理返回{error:"..."}而非标准choices格式
3. 多提供商API请求格式解析失败
4. API超时处理不完善

请分析:
1. 当前DSL设计的优缺点
2. 与LangChain、AutoGen相比的差距
3. 最重要的3个改进方向
4. 具体的DSL语法改进建议

请提供详细分析和建议。
"""
        
        print("📝 第一轮咨询: DSL设计分析...")
        
        chat_data = {
            "messages": [{"role": "user", "content": analysis_prompt}],
            "model": "google/gemini-2.5-pro"
        }
        
        response = requests.post(f"{BASE_URL}/chat/openrouter", json=chat_data, timeout=90)
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and result["choices"]:
                gemini_analysis = result["choices"][0]["message"]["content"]
                print("\n🎯 Gemini的DSL分析:")
                print("-" * 40)
                print(gemini_analysis)
                
                # 第二轮：深入讨论具体改进
                improvement_prompt = f"""
基于你的分析，我特别关注你提到的前3个改进方向。

请为每个改进方向设计具体的Kotlin DSL语法，要求:
1. 保持简洁性和直观性
2. 符合Kotlin语言特性 (扩展函数、DSL builder)
3. 易于LLM理解和生成代码
4. 提供从简单到复杂的渐进式用法

请提供:
- 具体的语法设计
- 使用示例代码
- 实现架构建议
- 与现有DSL的集成方式

重点关注如何解决我们发现的实际问题。
"""
                
                print("\n📝 第二轮咨询: 具体改进设计...")
                
                chat_data2 = {
                    "messages": [
                        {"role": "user", "content": analysis_prompt},
                        {"role": "assistant", "content": gemini_analysis},
                        {"role": "user", "content": improvement_prompt}
                    ],
                    "model": "google/gemini-2.5-pro"
                }
                
                response2 = requests.post(f"{BASE_URL}/chat/openrouter", json=chat_data2, timeout=90)
                
                if response2.status_code == 200:
                    result2 = response2.json()
                    if "choices" in result2 and result2["choices"]:
                        improvement_details = result2["choices"][0]["message"]["content"]
                        print("\n🎨 Gemini的具体改进建议:")
                        print("-" * 40)
                        print(improvement_details)
                        
                        return {
                            "analysis": gemini_analysis,
                            "improvements": improvement_details
                        }
                
                return {"analysis": gemini_analysis}
            else:
                print("❌ Gemini响应格式问题")
        else:
            print(f"❌ Gemini调用失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 与Gemini讨论失败: {e}")
    
    return None

def test_corrected_multi_provider():
    """测试修正后的多提供商调用"""
    print("\n\n🔄 测试修正后的多提供商调用")
    print("="*60)
    
    # 方法1: 分别调用然后对比
    print("方法1: 手动多提供商对比...")
    
    question = "Kotlin协程相比Java线程有什么优势？"
    results = {}
    
    # DeepSeek
    try:
        chat_data = {
            "messages": [{"role": "user", "content": question}],
            "model": "deepseek-chat"
        }
        response = requests.post(f"{BASE_URL}/chat/deepseek", json=chat_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and result["choices"]:
                results["DeepSeek"] = result["choices"][0]["message"]["content"][:100] + "..."
            
    except Exception as e:
        results["DeepSeek"] = f"错误: {e}"
    
    # Gemini
    try:
        chat_data = {
            "messages": [{"role": "user", "content": question}],
            "model": "google/gemini-2.5-pro"
        }
        response = requests.post(f"{BASE_URL}/chat/openrouter", json=chat_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and result["choices"]:
                results["Gemini"] = result["choices"][0]["message"]["content"][:100] + "..."
                
    except Exception as e:
        results["Gemini"] = f"错误: {e}"
    
    print("📊 多提供商对比结果:")
    for provider, answer in results.items():
        print(f"  {provider}: {answer}")

def create_dsl_improvement_plan():
    """基于实际使用经验创建DSL改进计划"""
    print("\n\n📋 基于实际使用经验的DSL改进计划")
    print("="*60)
    
    improvements = [
        {
            "问题": "模型名称不一致",
            "现状": "需要手动查询支持的模型名称",
            "解决方案": "DSL内置模型映射和智能选择",
            "新语法": "gemini(), gpt4(), claude() // 智能选择最佳模型",
            "优先级": "🔴 高"
        },
        {
            "问题": "错误处理不统一",
            "现状": "有时返回{error}, 有时返回choices",
            "解决方案": "DSL层统一错误处理和响应格式",
            "新语法": "result.onSuccess{}.onError{} // 链式错误处理",
            "优先级": "🔴 高"
        },
        {
            "问题": "缺少重试机制",
            "现状": "API调用失败就直接报错",
            "解决方案": "内置智能重试和降级",
            "新语法": '"问题" using provider.withRetry(3).withFallback(backup)',
            "优先级": "🟡 中"
        },
        {
            "问题": "缺少流式响应",
            "现状": "只支持一次性返回完整结果",
            "解决方案": "添加流式处理支持",
            "新语法": '"问题" streaming provider { chunk -> println(chunk) }',
            "优先级": "🟡 中"
        },
        {
            "问题": "缺少监控和调试",
            "现状": "无法监控调用性能和成功率",
            "解决方案": "内置监控和调试模式",
            "新语法": "provider.withDebug().withMetrics()",
            "优先级": "🟢 低"
        }
    ]
    
    print("🎯 DSL改进优先级列表:")
    for i, improvement in enumerate(improvements, 1):
        print(f"\n{i}. {improvement['优先级']} {improvement['问题']}")
        print(f"   现状: {improvement['现状']}")
        print(f"   方案: {improvement['解决方案']}")
        print(f"   语法: {improvement['新语法']}")
    
    return improvements

def main():
    """主测试流程"""
    print("🚀 DSL问题修复和改进讨论")
    print("=" * 70)
    
    # 1. 正确使用DSL
    use_dsl_correctly()
    
    # 2. 与Gemini讨论改进
    gemini_feedback = discuss_dsl_improvements_with_gemini()
    
    # 3. 测试多提供商功能
    test_corrected_multi_provider()
    
    # 4. 创建改进计划
    improvement_plan = create_dsl_improvement_plan()
    
    # 5. 保存结果
    results = {
        "gemini_feedback": gemini_feedback,
        "improvement_plan": improvement_plan,
        "timestamp": "2024-12-18",
        "status": "DSL问题诊断完成，获得Gemini专业建议"
    }
    
    with open("/root/code/dsl_improvement_plan.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 DSL改进计划已保存到: /root/code/dsl_improvement_plan.json")
    print("🎉 DSL使用问题诊断和改进讨论完成！")

if __name__ == "__main__":
    main()