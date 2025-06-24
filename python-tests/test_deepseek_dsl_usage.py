#!/usr/bin/env python3
"""
测试DeepSeek使用DSL的能力
通过给DeepSeek不同复杂度的任务，测试其对DSL的理解和使用正确性
"""

import os
import requests
import json
import time

# 禁用代理
for proxy_var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'all_proxy', 'ALL_PROXY']:
    os.environ.pop(proxy_var, None)

BASE_URL = "http://127.0.0.1:8080"

# DSL 文档和示例
DSL_DOCUMENTATION = """
# Kotlin LLM DSL 使用指南

## 核心设计理念
简洁、易懂、表达力强、扩展性好的DSL，用于便捷接入各种大模型

## 基础用法

### 1. 最简单的用法 - 一行代码
```kotlin
val answer = "你好，请介绍一下自己" using deepseek("api-key")
```

### 2. Provider创建函数
```kotlin
val provider = deepseek("api-key")  // DeepSeek
val provider = openrouter("api-key") // OpenRouter
val provider = mockProvider("TestMock") // Mock测试
```

### 3. 对话管理
```kotlin
val chat = conversation(provider) {
    system("你是一个Kotlin专家")
    ask("什么是协程？")
}
val followUp = chat.ask("协程有什么优势？")
```

### 4. 多模型对比
```kotlin
val comparison = compare(
    "解释什么是人工智能",
    mapOf(
        "deepseek" to deepseek("key1"),
        "openrouter" to openrouter("key2")
    )
)
```

### 5. Agent系统
```kotlin
val coder = agent("程序员", provider, "资深Kotlin开发者")
val advice = coder.solve("如何优化这段代码？")
```

### 6. 批量处理
```kotlin
val questions = listOf("什么是API？", "什么是数据库？")
val answers = questions.processAll(provider)
```

### 7. 回退策略
```kotlin
val resilient = primaryProvider.withFallback(backupProvider)
val safeAnswer = "问题" using resilient
```

### 8. 便利函数
```kotlin
// 快速问答
val quickAnswer = ask("今天天气怎么样？")

// 快速对比
val quickComp = quickCompare("解释什么是区块链")
```

## 重要注意事项
1. 使用 `using` 作为中缀函数连接问题和provider
2. conversation() 需要在花括号内使用 system() 和 ask()
3. agent() 创建后使用 solve() 方法
4. compare() 接受问题字符串和Map<String, LLMProvider>
5. 所有异步操作都用 suspend 修饰，需要在协程作用域内调用
"""

def test_deepseek_dsl_understanding():
    """测试DeepSeek对DSL的理解和使用能力"""
    print("🚀 测试DeepSeek对LLM DSL的理解和使用能力")
    
    # 测试用例：从简单到复杂
    test_cases = [
        {
            "name": "基础用法测试",
            "prompt": f"""
{DSL_DOCUMENTATION}

请使用上述Kotlin LLM DSL编写代码，完成以下任务：
写一个简单的函数，使用DeepSeek提供商询问"什么是机器学习？"

要求：
1. 使用DSL的最简单语法
2. 函数要完整可运行
3. 包含必要的导入和协程处理
""",
            "expected_patterns": ["using", "deepseek", "runBlocking", "suspend"]
        },
        
        {
            "name": "对话管理测试", 
            "prompt": f"""
{DSL_DOCUMENTATION}

使用Kotlin LLM DSL编写代码，创建一个对话场景：
1. 设置系统角色为"Python专家"
2. 询问"什么是装饰器？"
3. 继续询问"请举个例子"

要求使用conversation DSL语法，代码要完整。
""",
            "expected_patterns": ["conversation", "system", "ask", "Python专家"]
        },
        
        {
            "name": "多模型对比测试",
            "prompt": f"""
{DSL_DOCUMENTATION}

使用Kotlin LLM DSL编写代码，对比不同模型对"什么是区块链？"这个问题的回答：
1. 同时使用deepseek和openrouter两个提供商
2. 输出每个模型的回答
3. 使用compare函数

代码要完整可运行。
""",
            "expected_patterns": ["compare", "deepseek", "openrouter", "mapOf"]
        },
        
        {
            "name": "Agent系统测试",
            "prompt": f"""
{DSL_DOCUMENTATION}

使用Kotlin LLM DSL编写代码，创建一个编程助手Agent：
1. 角色设定为"资深Java开发者"
2. 让它解决"如何优化ArrayList的性能？"这个问题
3. 使用agent DSL语法

代码要完整。
""",
            "expected_patterns": ["agent", "solve", "资深Java开发者", "ArrayList"]
        },
        
        {
            "name": "复合功能测试",
            "prompt": f"""
{DSL_DOCUMENTATION}

使用Kotlin LLM DSL编写一个完整的程序，实现以下功能：
1. 创建一个Kotlin专家Agent
2. 让Agent解决"协程和线程的区别"问题
3. 同时用批量处理功能处理["什么是挂起函数？", "什么是协程作用域？"]这两个问题
4. 最后使用多模型对比功能对比不同模型对"Kotlin的优势"的看法

要求代码结构清晰，使用DSL的多种功能。
""",
            "expected_patterns": ["agent", "solve", "processAll", "compare", "suspend", "协程"]
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n=== 测试 {i}: {test_case['name']} ===")
        
        try:
            # 调用DeepSeek生成代码
            chat_data = {
                "messages": [{"role": "user", "content": test_case["prompt"]}],
                "model": "deepseek-chat"
            }
            
            response = requests.post(f"{BASE_URL}/chat/deepseek", json=chat_data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                generated_code = result["choices"][0]["message"]["content"]
                
                print(f"✅ DeepSeek生成代码成功")
                print(f"📝 生成的代码长度: {len(generated_code)} 字符")
                
                # 分析生成的代码质量
                correct_patterns = 0
                for pattern in test_case["expected_patterns"]:
                    if pattern in generated_code:
                        correct_patterns += 1
                        print(f"  ✅ 包含关键词: {pattern}")
                    else:
                        print(f"  ❌ 缺失关键词: {pattern}")
                
                accuracy = (correct_patterns / len(test_case["expected_patterns"])) * 100
                print(f"📊 准确率: {accuracy:.1f}% ({correct_patterns}/{len(test_case['expected_patterns'])})")
                
                results.append({
                    "test_name": test_case["name"],
                    "accuracy": accuracy,
                    "generated_code": generated_code,
                    "missing_patterns": [p for p in test_case["expected_patterns"] if p not in generated_code]
                })
                
                # 显示生成的代码片段
                print(f"🔍 生成代码预览:")
                print("```kotlin")
                print(generated_code[:300] + "..." if len(generated_code) > 300 else generated_code)
                print("```")
                
            else:
                print(f"❌ 请求失败: {response.status_code}")
                results.append({
                    "test_name": test_case["name"],
                    "accuracy": 0,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            results.append({
                "test_name": test_case["name"],
                "accuracy": 0,
                "error": str(e)
            })
        
        time.sleep(2)  # 避免请求过快
    
    # 总结报告
    print(f"\n{'='*50}")
    print("📊 DeepSeek DSL使用测试总结")
    print(f"{'='*50}")
    
    total_accuracy = 0
    successful_tests = 0
    
    for result in results:
        if "error" not in result:
            print(f"✅ {result['test_name']}: {result['accuracy']:.1f}%")
            total_accuracy += result['accuracy']
            successful_tests += 1
            
            if result['missing_patterns']:
                print(f"   ⚠️  缺失关键词: {', '.join(result['missing_patterns'])}")
        else:
            print(f"❌ {result['test_name']}: 失败 ({result['error']})")
    
    if successful_tests > 0:
        average_accuracy = total_accuracy / successful_tests
        print(f"\n🎯 总体准确率: {average_accuracy:.1f}%")
        
        if average_accuracy >= 90:
            print("🎉 DSL易用性优秀！DeepSeek能够准确理解和使用DSL")
        elif average_accuracy >= 70:
            print("✅ DSL易用性良好，但仍有优化空间")
        else:
            print("⚠️ DSL需要进一步优化，DeepSeek理解困难")
    
    return results

if __name__ == "__main__":
    results = test_deepseek_dsl_understanding()
    
    # 保存详细结果用于后续分析
    with open("/root/code/deepseek_dsl_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)