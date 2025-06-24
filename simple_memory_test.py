#!/usr/bin/env python3
"""
简单的记忆系统测试 - 不依赖重型依赖
"""

import sys
from pathlib import Path

# 检查是否能导入基本模块
print("🧪 测试基本Python模块导入...")

try:
    import numpy as np
    print("✅ numpy 可用")
except ImportError as e:
    print(f"❌ numpy 不可用: {e}")

try:
    from sklearn.metrics.pairwise import cosine_similarity
    print("✅ scikit-learn 可用")
except ImportError as e:
    print(f"❌ scikit-learn 不可用: {e}")

try:
    from sentence_transformers import SentenceTransformer
    print("✅ sentence-transformers 可用")
except ImportError as e:
    print(f"❌ sentence-transformers 不可用: {e}")

try:
    from pydantic import BaseModel
    print("✅ pydantic 可用")
except ImportError as e:
    print(f"❌ pydantic 不可用: {e}")

print("\n🔍 检查记忆系统基础结构...")

# 检查记忆系统基础文件是否存在
memory_system_path = Path("claude-memory-system")
if memory_system_path.exists():
    print(f"✅ 记忆系统目录存在: {memory_system_path}")
    
    key_files = [
        "claude_memory/__init__.py",
        "claude_memory/core/memory_manager.py", 
        "claude_memory/storage/vector_store.py",
        "claude_memory/models/memory.py"
    ]
    
    for file_path in key_files:
        full_path = memory_system_path / file_path
        if full_path.exists():
            print(f"✅ 关键文件存在: {file_path}")
        else:
            print(f"❌ 缺失关键文件: {file_path}")
else:
    print(f"❌ 记忆系统目录不存在: {memory_system_path}")

print("\n📊 测试结论:")
print("需要安装的依赖：scikit-learn, sentence-transformers")
print("建议使用API方式的embedding服务以避免本地模型依赖")