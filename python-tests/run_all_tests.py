#!/usr/bin/env python3
"""
运行所有测试的主脚本
"""

import subprocess
import sys
import os

def run_test(test_file):
    """运行单个测试文件"""
    print(f"\n{'='*60}")
    print(f"运行测试: {test_file}")
    print('='*60)
    
    try:
        result = subprocess.run([
            sys.executable, test_file
        ], capture_output=True, text=True, timeout=30)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"❌ 测试 {test_file} 超时")
        return False
    except Exception as e:
        print(f"❌ 运行测试 {test_file} 时出错: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始运行LLM服务集成测试套件")
    
    # 测试文件列表
    test_files = [
        "test_health.py",
        "test_models.py", 
        "test_chat_basic.py",
        "test_multiple_chat.py"
    ]
    
    # 检查所有测试文件是否存在
    missing_files = []
    for test_file in test_files:
        if not os.path.exists(test_file):
            missing_files.append(test_file)
    
    if missing_files:
        print(f"❌ 缺少测试文件: {missing_files}")
        sys.exit(1)
    
    # 运行所有测试
    passed = 0
    failed = 0
    
    for test_file in test_files:
        if run_test(test_file):
            passed += 1
            print(f"✅ {test_file} 通过")
        else:
            failed += 1
            print(f"❌ {test_file} 失败")
    
    # 输出总结
    print(f"\n{'='*60}")
    print("测试总结")
    print('='*60)
    print(f"总测试数: {len(test_files)}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    
    if failed == 0:
        print("🎉 所有测试都通过了！")
        sys.exit(0)
    else:
        print("💥 有测试失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()