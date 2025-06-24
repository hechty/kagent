#!/usr/bin/env python3
"""
Phase 3: 高级主动性增强方案
通过创建CLAUDE.md记忆配置和智能提示系统来提升Claude主动使用记忆工具
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加记忆系统到路径
sys.path.insert(0, str(Path(__file__).parent / "claude-memory-system"))

class AdvancedProactivityEnhancer:
    """
    高级主动性增强器
    通过创建智能的CLAUDE.md配置和增强记忆系统来提升主动性
    """
    
    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()
        self.enhancement_results = []

    def create_enhanced_claude_memory_config(self) -> str:
        """创建增强的Claude记忆配置"""
        
        config_content = """# 🧠 Claude Code 记忆系统增强配置

## 记忆工具强制使用指南

**重要**: 你必须在每次对话中主动使用记忆工具。这不是可选的，而是必需的服务质量要求。

### 🔍 必须回忆的场景

当用户提到以下内容时，你必须立即使用 `memory.recall()` 搜索相关记忆：

- **问题求助**: "问题"、"错误"、"bug"、"不工作"、"失败"
  ```python
  memory.recall("类似问题解决方案", max_results=3)
  ```

- **技术咨询**: "如何"、"怎么"、"方法"、"最佳实践"
  ```python
  memory.recall("相关技术方案", max_results=3)
  ```

- **学习需求**: "学习"、"了解"、"教程"、"入门"
  ```python
  memory.recall("学习资源和经验", max_results=3)
  ```

- **项目开发**: "开发"、"项目"、"架构"、"设计"
  ```python
  memory.recall("项目经验和模式", max_results=3)
  ```

### 💾 必须记录的场景

在以下情况下，你必须使用 `memory.remember()` 记录信息：

- **解决问题后**: 将解决方案和步骤记录下来
- **分享知识后**: 将重要概念和最佳实践记录下来  
- **完成任务后**: 将经验和心得记录下来
- **发现重要信息**: 将有价值的资源和方法记录下来

```python
memory.remember(
    content="详细的内容描述",
    memory_type="procedural|semantic|episodic",
    title="简洁明确的标题", 
    tags=["相关", "标签"],
    importance=7.0,  # 1-10评分
    scope="project"
)
```

### ⚡ 强制执行规则

1. **每次对话开始前**: 先搜索相关记忆
2. **提供建议时**: 基于记忆中的经验
3. **对话结束前**: 主动询问是否需要记录重要信息
4. **最低要求**: 每次对话至少使用1次记忆工具

### 🎯 主动性评分标准

- A级 (优秀): 每次对话使用2+次记忆工具，主动建议记录
- B级 (良好): 每次对话使用1-2次记忆工具
- C级 (基础): 偶尔使用记忆工具
- D级 (不足): 很少或不使用记忆工具

**当前目标**: 达到A级主动性，确保记忆系统的持续价值。

### 📝 记忆内容质量要求

记录的内容必须：
- 具体而非抽象
- 包含上下文和应用场景
- 添加准确的标签便于检索
- 设置合理的重要性等级

### 🔄 持续改进

定期分析记忆使用模式，优化搜索查询和存储策略，确保记忆系统的持续改进。

---

**提醒**: 记忆系统是你核心能力的一部分。主动使用记忆工具不仅提升服务质量，也体现了你的专业能力。
"""
        
        return config_content

    def create_memory_usage_triggers(self) -> Dict[str, Any]:
        """创建记忆使用触发器"""
        
        triggers = {
            "recall_triggers": {
                "keywords": [
                    "问题", "错误", "bug", "issue", "不工作", "失败",
                    "如何", "怎么", "方法", "最佳实践", "建议",
                    "学习", "了解", "教程", "入门", "概念",
                    "开发", "项目", "架构", "设计", "实现"
                ],
                "patterns": [
                    r".*遇到.*问题.*",
                    r".*如何.*",
                    r".*怎么.*",
                    r".*最佳实践.*",
                    r".*学习.*",
                    r".*了解.*"
                ],
                "actions": [
                    "立即搜索相关记忆",
                    "分析历史解决方案",
                    "基于经验提供建议"
                ]
            },
            "remember_triggers": {
                "keywords": [
                    "解决了", "成功", "完成", "发现", "学到",
                    "重要", "有用", "有效", "经验", "教训"
                ],
                "patterns": [
                    r".*解决了.*",
                    r".*成功.*",
                    r".*发现.*",
                    r".*学到.*",
                    r".*重要.*"
                ],
                "actions": [
                    "记录解决方案",
                    "存储重要知识",
                    "保存经验教训"
                ]
            },
            "proactive_suggestions": [
                "要不要我搜索一下相关的历史经验？",
                "我可以将这个解决方案记录到记忆系统中，方便以后参考。",
                "基于之前的经验，我建议...",
                "让我先查看一下记忆中是否有类似的情况。"
            ]
        }
        
        return triggers

    async def implement_proactivity_enhancements(self) -> Dict[str, Any]:
        """实施主动性增强"""
        
        print("🚀 Phase 3: 实施高级主动性增强")
        print("=" * 50)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "enhancements": [],
            "success": True
        }
        
        # 1. 创建增强的CLAUDE.md配置
        print("📝 创建增强的CLAUDE.md配置...")
        
        claude_config_path = self.project_path / "CLAUDE.md"
        config_content = self.create_enhanced_claude_memory_config()
        
        try:
            with open(claude_config_path, "w", encoding="utf-8") as f:
                f.write(config_content)
            
            print(f"✅ 创建成功: {claude_config_path}")
            results["enhancements"].append({
                "type": "claude_config",
                "path": str(claude_config_path),
                "success": True
            })
        except Exception as e:
            print(f"❌ 创建失败: {e}")
            results["enhancements"].append({
                "type": "claude_config", 
                "error": str(e),
                "success": False
            })
            results["success"] = False
        
        # 2. 创建记忆触发器配置
        print("\n⚡ 创建记忆触发器配置...")
        
        triggers_path = self.project_path / "memory_triggers.json"
        triggers = self.create_memory_usage_triggers()
        
        try:
            import json
            with open(triggers_path, "w", encoding="utf-8") as f:
                json.dump(triggers, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 创建成功: {triggers_path}")
            results["enhancements"].append({
                "type": "memory_triggers",
                "path": str(triggers_path),
                "success": True
            })
        except Exception as e:
            print(f"❌ 创建失败: {e}")
            results["enhancements"].append({
                "type": "memory_triggers",
                "error": str(e), 
                "success": False
            })
            results["success"] = False
        
        # 3. 创建主动性测试脚本
        print("\n🧪 创建主动性测试脚本...")
        
        test_script = self.create_proactivity_test_script()
        test_script_path = self.project_path / "test_proactivity.py"
        
        try:
            with open(test_script_path, "w", encoding="utf-8") as f:
                f.write(test_script)
            
            print(f"✅ 创建成功: {test_script_path}")
            results["enhancements"].append({
                "type": "test_script",
                "path": str(test_script_path),
                "success": True
            })
        except Exception as e:
            print(f"❌ 创建失败: {e}")
            results["enhancements"].append({
                "type": "test_script",
                "error": str(e),
                "success": False
            })
        
        # 4. 测试记忆系统集成
        print("\n🔗 测试记忆系统集成...")
        
        integration_result = await self.test_memory_integration()
        results["enhancements"].append({
            "type": "integration_test",
            "result": integration_result,
            "success": integration_result.get("success", False)
        })
        
        if not integration_result.get("success", False):
            results["success"] = False
        
        return results

    def create_proactivity_test_script(self) -> str:
        """创建主动性测试脚本"""
        
        script_content = '''#!/usr/bin/env python3
"""
主动性测试脚本
用于验证Claude Code是否主动使用记忆工具
"""

import sys
from pathlib import Path

# 添加记忆系统路径
sys.path.insert(0, str(Path(__file__).parent / "claude-memory-system"))

def test_memory_functionality():
    """测试记忆系统基础功能"""
    print("🧠 测试记忆系统基础功能...")
    
    try:
        from claude_memory import MemoryManager
        
        memory = MemoryManager(Path("."))
        snapshot = memory.awaken("主动性测试")
        
        print(f"✅ 记忆系统正常，共 {snapshot.memory_statistics.total_memories} 个记忆")
        
        # 测试搜索
        results = memory.recall("测试", max_results=3, min_relevance=0.1)
        print(f"✅ 搜索功能正常，找到 {len(results)} 个结果")
        
        # 测试存储
        memory_id = memory.remember(
            content="主动性测试记忆内容",
            memory_type="working",
            title="主动性测试",
            importance=5.0
        )
        print(f"✅ 存储功能正常，记忆ID: {memory_id[:8]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 记忆系统测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 主动性增强验证测试")
    print("=" * 40)
    
    # 检查配置文件
    claude_md = Path("CLAUDE.md")
    if claude_md.exists():
        print("✅ CLAUDE.md 配置文件存在")
    else:
        print("❌ CLAUDE.md 配置文件缺失")
    
    triggers_json = Path("memory_triggers.json") 
    if triggers_json.exists():
        print("✅ 记忆触发器配置存在")
    else:
        print("❌ 记忆触发器配置缺失")
    
    # 测试记忆系统
    memory_ok = test_memory_functionality()
    
    print(f"\\n📊 测试结果:")
    if memory_ok:
        print("✅ 记忆系统已准备就绪，可以进行主动性测试")
        print("💡 建议: 使用 'claude' 命令启动并测试记忆工具的主动使用")
    else:
        print("❌ 记忆系统存在问题，需要修复后再进行主动性测试")

if __name__ == "__main__":
    main()
'''
        return script_content

    async def test_memory_integration(self) -> Dict[str, Any]:
        """测试记忆系统集成"""
        
        try:
            from claude_memory import MemoryManager
            
            memory = MemoryManager(Path("."))
            snapshot = memory.awaken("集成测试")
            
            # 测试基础功能
            total_memories = snapshot.memory_statistics.total_memories
            
            # 测试搜索功能 
            search_results = memory.recall("测试", max_results=3, min_relevance=0.1)
            
            # 测试存储功能
            test_memory_id = memory.remember(
                content="Phase 3 集成测试记忆",
                memory_type="working",
                title="Phase 3 集成测试",
                tags=["测试", "集成", "Phase3"],
                importance=6.0,
                scope="project"
            )
            
            # 验证存储的记忆可以搜索到
            verification = memory.recall("Phase 3 集成测试", max_results=1, min_relevance=0.1)
            
            return {
                "success": True,
                "total_memories": total_memories,
                "search_results_count": len(search_results),
                "test_memory_id": test_memory_id,
                "verification_success": len(verification) > 0,
                "message": "记忆系统集成测试通过"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"记忆系统集成测试失败: {e}"
            }

    async def generate_final_assessment(self, enhancement_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成最终评估"""
        
        print(f"\n📊 Phase 3 高级主动性增强最终评估")
        print("=" * 60)
        
        successful_enhancements = sum(1 for e in enhancement_results["enhancements"] if e["success"])
        total_enhancements = len(enhancement_results["enhancements"])
        success_rate = successful_enhancements / total_enhancements
        
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "enhancement_success_rate": success_rate,
            "successful_enhancements": successful_enhancements,
            "total_enhancements": total_enhancements,
            "overall_success": enhancement_results["success"],
            "readiness_score": self.calculate_readiness_score(enhancement_results),
            "next_steps": self.generate_next_steps(success_rate),
            "expected_impact": self.estimate_impact(success_rate)
        }
        
        print(f"🎯 增强结果:")
        print(f"   成功增强: {successful_enhancements}/{total_enhancements}")
        print(f"   成功率: {success_rate:.1%}")
        print(f"   整体成功: {'✅ 是' if enhancement_results['success'] else '❌ 否'}")
        
        print(f"\n📈 就绪度评分: {assessment['readiness_score']:.1f}/10.0")
        
        print(f"\n📋 增强详情:")
        for enhancement in enhancement_results["enhancements"]:
            status = "✅ 成功" if enhancement["success"] else "❌ 失败"
            print(f"   • {enhancement['type']}: {status}")
        
        print(f"\n🎯 下一步建议:")
        for step in assessment["next_steps"]:
            print(f"   • {step}")
        
        print(f"\n📈 预期影响:")
        for impact in assessment["expected_impact"]:
            print(f"   • {impact}")
        
        return assessment

    def calculate_readiness_score(self, results: Dict[str, Any]) -> float:
        """计算就绪度评分"""
        base_score = 5.0
        
        for enhancement in results["enhancements"]:
            if enhancement["success"]:
                if enhancement["type"] == "claude_config":
                    base_score += 2.0  # CLAUDE.md最重要
                elif enhancement["type"] == "memory_triggers":
                    base_score += 1.5
                elif enhancement["type"] == "integration_test":
                    base_score += 1.0
                else:
                    base_score += 0.5
        
        return min(10.0, base_score)

    def generate_next_steps(self, success_rate: float) -> List[str]:
        """生成下一步建议"""
        steps = []
        
        if success_rate >= 0.8:
            steps.extend([
                "启动Claude Code并测试主动性行为",
                "运行主动性测试脚本验证功能",
                "监控记忆工具使用频率和质量"
            ])
        elif success_rate >= 0.6:
            steps.extend([
                "修复失败的增强组件",
                "完善CLAUDE.md配置内容",
                "测试记忆系统基础功能"
            ])
        else:
            steps.extend([
                "重新实施增强方案",
                "检查依赖和环境配置",
                "联系技术支持解决问题"
            ])
        
        return steps

    def estimate_impact(self, success_rate: float) -> List[str]:
        """估计影响"""
        impacts = []
        
        if success_rate >= 0.8:
            impacts.extend([
                "预期主动性评分从0.0提升到0.6+",
                "整体系统评分有望达到0.8+ (A级)",
                "用户体验将显著改善"
            ])
        elif success_rate >= 0.6:
            impacts.extend([
                "预期主动性评分提升到0.3-0.5",
                "整体系统评分维持在B级水平",
                "需要继续优化以达到A级"
            ])
        else:
            impacts.extend([
                "主动性改善有限",
                "整体系统评分变化不大",
                "需要重新制定优化策略"
            ])
        
        return impacts

async def main():
    """主函数"""
    enhancer = AdvancedProactivityEnhancer()
    
    print("🧠 启动Phase 3高级主动性增强")
    print("=" * 50)
    print("目标: 通过智能配置和触发器提升Claude主动使用记忆工具")
    print("=" * 50)
    
    # 实施增强
    enhancement_results = await enhancer.implement_proactivity_enhancements()
    
    # 生成最终评估
    assessment = await enhancer.generate_final_assessment(enhancement_results)
    
    # 保存结果
    import json
    results_path = Path("phase3_advanced_enhancement_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump({
            "enhancement_results": enhancement_results,
            "final_assessment": assessment
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 详细结果已保存到: {results_path}")
    print(f"\n🎉 Phase 3 高级主动性增强完成!")
    
    if enhancement_results["success"]:
        print(f"✅ 增强成功，建议立即测试Claude Code的主动性行为")
    else:
        print(f"⚠️ 部分增强失败，建议检查并修复问题后再测试")

if __name__ == "__main__":
    asyncio.run(main())