#!/usr/bin/env python3
"""
复杂多步骤任务的记忆管理测试
测试记忆系统在复杂工作流中的表现
"""

import sys
import asyncio
import time
import json
from pathlib import Path
from typing import List, Dict, Any
import random

# 添加记忆系统到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "claude-memory-system"))

from claude_memory import MemoryManager

class ComplexScenarioTester:
    """复杂场景测试器"""
    
    def __init__(self, project_path: Path):
        self.memory = MemoryManager(project_path=project_path)
        self.scenario_results = []
        
    async def ensure_memory_sync(self):
        """确保记忆同步到向量存储"""
        # 苏醒系统
        snapshot = self.memory.awaken("复杂场景测试")
        
        # 手动同步文件存储到向量存储
        all_memories = self.memory._file_store.load_all_memories()
        for mem in all_memories:
            if mem.id not in self.memory._vector_store._memory_cache:
                self.memory._vector_store.store_memory(mem)
        
        print(f"✅ 记忆系统已同步，总记忆数: {len(all_memories)}")
        return len(all_memories)
    
    async def test_multi_step_project_development(self):
        """测试多步骤项目开发场景"""
        print("\n🚀 测试场景1: 多步骤Web应用开发")
        print("-" * 50)
        
        # 模拟一个完整的Web应用开发流程
        development_steps = [
            {
                "step": "需求分析",
                "action": "分析用户需求，设计系统架构",
                "search_query": "web应用架构设计",
                "memory_content": """
Web应用需求分析结果：
- 用户管理系统：注册、登录、权限控制
- 内容管理：文章发布、编辑、删除
- 评论系统：用户评论、点赞、回复
- 搜索功能：全文搜索、标签筛选
- 数据统计：用户行为分析、内容热度

技术选型：
- 前端：React + TypeScript + Tailwind CSS
- 后端：Node.js + Express + PostgreSQL
- 部署：Docker + Kubernetes + AWS
                """,
                "tags": ["需求分析", "架构设计", "web应用"]
            },
            {
                "step": "数据库设计",
                "action": "设计数据库表结构",
                "search_query": "数据库设计最佳实践",
                "memory_content": """
Web应用数据库设计：

用户表 (users):
- id (PK), username, email, password_hash
- created_at, updated_at, last_login
- role (admin/editor/user), status (active/inactive)

文章表 (articles):
- id (PK), title, content, author_id (FK)
- published_at, updated_at, status (draft/published)
- category_id (FK), view_count, like_count

评论表 (comments):
- id (PK), article_id (FK), user_id (FK)
- content, parent_id (FK), created_at
- status (approved/pending/deleted)

索引优化：
- articles: (author_id, published_at), (category_id)
- comments: (article_id, created_at), (user_id)
                """,
                "tags": ["数据库设计", "PostgreSQL", "索引优化"]
            },
            {
                "step": "API开发",
                "action": "开发REST API接口",
                "search_query": "Node.js Express API开发",
                "memory_content": """
Web应用API设计：

用户认证 API:
POST /api/auth/register - 用户注册
POST /api/auth/login - 用户登录
POST /api/auth/logout - 用户登出
GET /api/auth/profile - 获取用户信息

文章管理 API:
GET /api/articles - 获取文章列表 (分页+筛选)
GET /api/articles/:id - 获取文章详情
POST /api/articles - 创建文章 (需认证)
PUT /api/articles/:id - 更新文章 (需权限)
DELETE /api/articles/:id - 删除文章 (需权限)

评论系统 API:
GET /api/articles/:id/comments - 获取评论列表
POST /api/articles/:id/comments - 添加评论 (需认证)
PUT /api/comments/:id - 更新评论 (需权限)
DELETE /api/comments/:id - 删除评论 (需权限)

中间件实现：
- 身份认证：JWT token验证
- 权限控制：基于角色的访问控制
- 输入验证：参数校验和XSS防护
- 错误处理：统一错误响应格式
                """,
                "tags": ["API开发", "Node.js", "Express", "JWT", "权限控制"]
            },
            {
                "step": "前端开发",
                "action": "开发React前端界面",
                "search_query": "React TypeScript最佳实践",
                "memory_content": """
React前端开发实现：

项目结构：
src/
  components/ - 可复用组件
    UI/ - 基础UI组件 (Button, Input, Modal)
    Layout/ - 布局组件 (Header, Sidebar, Footer)
  pages/ - 页面组件
    Auth/ - 登录注册页面
    Articles/ - 文章相关页面
    Profile/ - 用户中心页面
  hooks/ - 自定义hooks
    useAuth.ts - 认证状态管理
    useAPI.ts - API调用封装
  store/ - 状态管理 (Redux Toolkit)
  utils/ - 工具函数

关键实现：
- 路由管理：React Router v6
- 状态管理：Redux Toolkit + RTK Query
- 样式方案：Tailwind CSS + CSS Modules
- 表单处理：React Hook Form + Yup验证
- 权限控制：路由守卫 + 组件级权限
                """,
                "tags": ["React", "TypeScript", "前端开发", "状态管理"]
            },
            {
                "step": "测试开发",
                "action": "编写单元测试和集成测试",
                "search_query": "Node.js React测试最佳实践",
                "memory_content": """
Web应用测试策略：

后端测试 (Jest + Supertest):
- 单元测试：模型验证、工具函数
- API测试：每个端点的CRUD操作
- 集成测试：数据库交互、认证流程
- 中间件测试：权限验证、错误处理

前端测试 (Jest + React Testing Library):
- 组件测试：渲染、用户交互、状态变化
- 页面测试：路由导航、数据获取
- Hook测试：自定义hooks的逻辑
- 端到端测试：Cypress完整流程测试

测试覆盖率目标：
- 后端API：90%以上代码覆盖率
- 前端组件：85%以上覆盖率
- 关键业务流程：100%覆盖

CI/CD集成：
- GitHub Actions自动化测试
- 代码质量检查：ESLint + Prettier
- 安全扫描：npm audit + Snyk
                """,
                "tags": ["测试开发", "Jest", "React Testing Library", "CI/CD"]
            },
            {
                "step": "部署上线",
                "action": "部署到生产环境",
                "search_query": "Docker Kubernetes部署",
                "memory_content": """
Web应用部署方案：

容器化配置：
- Frontend Dockerfile：多阶段构建，nginx静态托管
- Backend Dockerfile：Node.js运行时优化
- PostgreSQL：官方镜像+持久化存储
- Redis：缓存和会话存储

Kubernetes部署：
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: webapp-backend
  template:
    spec:
      containers:
      - name: backend
        image: webapp-backend:latest
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: webapp-secrets
              key: database-url

服务配置：
- Ingress：域名路由和SSL终止
- Service：负载均衡和服务发现
- ConfigMap：应用配置管理
- Secret：敏感信息加密存储

监控告警：
- Prometheus：指标收集
- Grafana：可视化监控面板
- AlertManager：告警规则和通知
                """,
                "tags": ["部署", "Docker", "Kubernetes", "监控"]
            }
        ]
        
        step_memories = []
        context_evolution = []
        
        for i, step_info in enumerate(development_steps, 1):
            print(f"\n步骤 {i}: {step_info['step']}")
            
            # 1. 基于前面的记忆搜索相关经验
            if step_memories:
                print("  📚 搜索相关记忆...")
                
                # 构建基于上下文的搜索查询
                context_tags = []
                for mem in step_memories[-2:]:  # 使用最近2个记忆作为上下文
                    context_tags.extend(mem.memory.tags)
                
                enhanced_query = f"{step_info['search_query']} {' '.join(set(context_tags[-5:]))}"
                search_results = self.memory.recall(enhanced_query, max_results=3, min_relevance=0.1)
                
                print(f"     查询: {step_info['search_query']}")
                print(f"     上下文增强: {enhanced_query}")
                print(f"     找到 {len(search_results)} 个相关记忆")
                
                # 分析上下文连贯性
                if search_results:
                    for result in search_results:
                        context_overlap = len(set(context_tags) & set(result.memory.tags))
                        print(f"       - {result.memory.title} (相关性: {result.relevance_score:.3f}, 上下文重叠: {context_overlap})")
            
            # 2. 存储当前步骤的记忆
            print("  💾 存储步骤记忆...")
            memory_id = self.memory.remember(
                content=step_info["memory_content"],
                memory_type="episodic",
                title=f"Web应用开发 - {step_info['step']}",
                tags=step_info["tags"] + ["web应用开发", f"第{i}步"],
                importance=8.0 + (i * 0.2),  # 递增重要性
                scope="project"
            )
            
            # 获取刚存储的记忆
            stored_memory = self.memory._file_store.load_memory(memory_id)
            if stored_memory:
                # 确保在向量存储中
                if memory_id not in self.memory._vector_store._memory_cache:
                    self.memory._vector_store.store_memory(stored_memory)
                
                step_memories.append(type('MemoryResult', (), {
                    'memory': stored_memory,
                    'relevance_score': 1.0
                })())
            
            # 3. 分析当前上下文状态
            current_context = {
                "step": i,
                "action": step_info["action"],
                "accumulated_tags": list(set(sum([mem.memory.tags for mem in step_memories], []))),
                "memory_count": len(step_memories)
            }
            context_evolution.append(current_context)
            
            print(f"     存储记忆ID: {memory_id[:8]}...")
            print(f"     累积标签数: {len(current_context['accumulated_tags'])}")
            
            # 4. 基于当前上下文获取建议
            if i > 2:  # 从第3步开始获取建议
                suggestions = self.memory.suggest(f"正在开发Web应用，已完成{step_info['step']}，下一步计划")
                if suggestions:
                    print(f"  💡 智能建议:")
                    for j, suggestion in enumerate(suggestions[:2], 1):
                        print(f"       {j}. {suggestion.action}")
        
        # 分析整个开发流程的记忆连贯性
        print(f"\n📊 开发流程记忆分析:")
        
        # 计算步骤间的语义连贯性
        coherence_scores = []
        for i in range(len(step_memories) - 1):
            tags1 = set(step_memories[i].memory.tags)
            tags2 = set(step_memories[i+1].memory.tags)
            
            # 计算标签重叠度
            overlap = len(tags1 & tags2)
            union = len(tags1 | tags2)
            coherence = overlap / union if union > 0 else 0
            
            coherence_scores.append(coherence)
            print(f"  步骤{i+1}→{i+2} 连贯性: {coherence:.3f}")
        
        avg_coherence = sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0
        
        # 测试跨步骤的记忆检索
        print(f"\n🔍 跨步骤记忆检索测试:")
        cross_step_queries = [
            "数据库API集成",
            "前端后端对接",
            "测试部署流程",
            "完整开发流程"
        ]
        
        retrieval_accuracy = []
        for query in cross_step_queries:
            results = self.memory.recall(query, max_results=5, min_relevance=0.1)
            
            # 检查是否能找到相关的开发步骤
            found_steps = set()
            for result in results:
                if "web应用开发" in result.memory.tags:
                    for tag in result.memory.tags:
                        if tag.startswith("第") and tag.endswith("步"):
                            found_steps.add(tag)
            
            accuracy = len(found_steps) / len(development_steps)
            retrieval_accuracy.append(accuracy)
            
            print(f"  '{query}': 找到 {len(results)} 个结果, 覆盖 {len(found_steps)} 个开发步骤")
        
        avg_retrieval_accuracy = sum(retrieval_accuracy) / len(retrieval_accuracy)
        
        return {
            "scenario": "多步骤Web应用开发",
            "total_steps": len(development_steps),
            "memories_created": len(step_memories),
            "avg_coherence": avg_coherence,
            "avg_retrieval_accuracy": avg_retrieval_accuracy,
            "context_evolution": context_evolution
        }
    
    async def test_knowledge_domain_integration(self):
        """测试知识领域整合场景"""
        print("\n🧠 测试场景2: 知识领域整合应用")
        print("-" * 50)
        
        # 模拟需要整合多个技术领域的复杂任务
        integration_tasks = [
            {
                "task": "AI驱动的推荐系统架构",
                "domains": ["机器学习", "分布式系统", "数据库"],
                "search_queries": [
                    "机器学习推荐算法",
                    "分布式计算架构",
                    "大数据存储方案"
                ]
            },
            {
                "task": "微服务架构的监控系统",
                "domains": ["容器化", "监控", "分布式系统"],
                "search_queries": [
                    "Kubernetes服务监控",
                    "分布式日志收集",
                    "微服务链路追踪"
                ]
            },
            {
                "task": "高性能数据分析平台",
                "domains": ["数据库", "性能优化", "机器学习"],
                "search_queries": [
                    "数据库性能优化",
                    "大数据处理框架",
                    "实时数据分析"
                ]
            }
        ]
        
        integration_results = []
        
        for task_info in integration_tasks:
            print(f"\n任务: {task_info['task']}")
            print(f"涉及领域: {', '.join(task_info['domains'])}")
            
            # 对每个领域进行记忆搜索
            domain_memories = {}
            total_relevance = 0
            found_domains = set()
            
            for domain, query in zip(task_info['domains'], task_info['search_queries']):
                print(f"\n  搜索 {domain}: '{query}'")
                
                results = self.memory.recall(query, max_results=3, min_relevance=0.1)
                domain_memories[domain] = results
                
                if results:
                    best_result = results[0]
                    total_relevance += best_result.relevance_score
                    
                    # 检查找到的记忆是否真的属于该领域
                    for tag in best_result.memory.tags:
                        if domain.lower() in tag.lower() or any(d.lower() in tag.lower() for d in task_info['domains']):
                            found_domains.add(domain)
                            break
                    
                    print(f"    最佳匹配: {best_result.memory.title}")
                    print(f"    相关性: {best_result.relevance_score:.3f}")
                    print(f"    标签: {best_result.memory.tags}")
                else:
                    print(f"    未找到相关记忆")
            
            # 分析领域整合度
            domain_coverage = len(found_domains) / len(task_info['domains'])
            avg_relevance = total_relevance / len(task_info['domains']) if task_info['domains'] else 0
            
            # 尝试跨领域整合搜索
            print(f"\n  跨领域整合搜索:")
            integrated_query = " ".join(task_info['domains'])
            integrated_results = self.memory.recall(integrated_query, max_results=5, min_relevance=0.05)
            
            cross_domain_score = 0
            for result in integrated_results:
                # 计算该记忆涵盖多少个目标领域
                covered_domains = 0
                for domain in task_info['domains']:
                    if any(domain.lower() in tag.lower() for tag in result.memory.tags):
                        covered_domains += 1
                
                cross_domain_score += covered_domains / len(task_info['domains'])
            
            cross_domain_avg = cross_domain_score / len(integrated_results) if integrated_results else 0
            
            result = {
                "task": task_info['task'],
                "domain_coverage": domain_coverage,
                "avg_relevance": avg_relevance,
                "cross_domain_score": cross_domain_avg,
                "memories_found": sum(len(memories) for memories in domain_memories.values())
            }
            
            integration_results.append(result)
            
            print(f"  📊 结果: 领域覆盖{domain_coverage:.1%}, 平均相关性{avg_relevance:.3f}, 跨域整合{cross_domain_avg:.3f}")
        
        return integration_results
    
    async def test_long_term_memory_persistence(self):
        """测试长期记忆持久化场景"""
        print("\n⏰ 测试场景3: 长期记忆持久化")
        print("-" * 50)
        
        # 模拟长期使用过程中的记忆积累和检索
        print("  📚 分析现有记忆分布...")
        
        # 分析记忆的时间分布和类型分布
        all_memories = self.memory._file_store.load_all_memories()
        
        memory_stats = {
            "total": len(all_memories),
            "by_type": {},
            "by_scope": {},
            "by_importance": {"high": 0, "medium": 0, "low": 0},
            "avg_importance": 0
        }
        
        importance_sum = 0
        for memory in all_memories:
            # 类型分布
            mem_type = memory.memory_type.value
            memory_stats["by_type"][mem_type] = memory_stats["by_type"].get(mem_type, 0) + 1
            
            # 范围分布
            scope = memory.scope.value
            memory_stats["by_scope"][scope] = memory_stats["by_scope"].get(scope, 0) + 1
            
            # 重要性分布
            importance = memory.importance
            importance_sum += importance
            
            if importance >= 8.0:
                memory_stats["by_importance"]["high"] += 1
            elif importance >= 5.0:
                memory_stats["by_importance"]["medium"] += 1
            else:
                memory_stats["by_importance"]["low"] += 1
        
        memory_stats["avg_importance"] = importance_sum / len(all_memories) if all_memories else 0
        
        print(f"    总记忆数: {memory_stats['total']}")
        print(f"    类型分布: {memory_stats['by_type']}")
        print(f"    范围分布: {memory_stats['by_scope']}")
        print(f"    重要性分布: {memory_stats['by_importance']}")
        print(f"    平均重要性: {memory_stats['avg_importance']:.2f}")
        
        # 测试记忆的时间衰减效应
        print("\n  🕐 测试记忆检索的时间效应...")
        
        # 模拟不同时期的查询
        time_based_queries = [
            "最近的编程经验",
            "Python性能优化",
            "系统架构设计",
            "数据库优化技巧"
        ]
        
        retrieval_consistency = []
        for query in time_based_queries:
            # 多次搜索同样的查询，检查结果一致性
            results_sets = []
            for _ in range(3):
                results = self.memory.recall(query, max_results=5, min_relevance=0.1)
                results_sets.append([r.memory.id for r in results])
            
            # 计算结果一致性
            if results_sets:
                first_set = set(results_sets[0])
                consistency_scores = []
                for result_set in results_sets[1:]:
                    overlap = len(first_set & set(result_set))
                    consistency = overlap / len(first_set | set(result_set)) if (first_set | set(result_set)) else 1.0
                    consistency_scores.append(consistency)
                
                avg_consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 1.0
                retrieval_consistency.append(avg_consistency)
                
                print(f"    '{query}': 一致性 {avg_consistency:.3f}")
        
        avg_retrieval_consistency = sum(retrieval_consistency) / len(retrieval_consistency) if retrieval_consistency else 0
        
        return {
            "memory_stats": memory_stats,
            "retrieval_consistency": avg_retrieval_consistency,
            "persistence_quality": memory_stats["avg_importance"] / 10.0  # 归一化到0-1
        }
    
    async def run_comprehensive_complex_test(self):
        """运行综合复杂场景测试"""
        print("🧪 开始复杂多步骤任务记忆管理测试")
        print("=" * 60)
        
        # 确保记忆系统同步
        total_memories = await self.ensure_memory_sync()
        
        # 运行各个测试场景
        scenario1_result = await self.test_multi_step_project_development()
        scenario2_result = await self.test_knowledge_domain_integration()
        scenario3_result = await self.test_long_term_memory_persistence()
        
        # 综合评估
        print("\n📊 综合复杂场景测试结果")
        print("=" * 50)
        
        # 场景1评估 - 多步骤开发
        print(f"场景1 - 多步骤开发:")
        print(f"  步骤连贯性: {scenario1_result['avg_coherence']:.3f}")
        print(f"  跨步骤检索准确性: {scenario1_result['avg_retrieval_accuracy']:.3f}")
        
        # 场景2评估 - 知识整合
        integration_scores = [r['domain_coverage'] for r in scenario2_result]
        relevance_scores = [r['avg_relevance'] for r in scenario2_result]
        cross_domain_scores = [r['cross_domain_score'] for r in scenario2_result]
        
        avg_integration = sum(integration_scores) / len(integration_scores) if integration_scores else 0
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
        avg_cross_domain = sum(cross_domain_scores) / len(cross_domain_scores) if cross_domain_scores else 0
        
        print(f"场景2 - 知识领域整合:")
        print(f"  领域覆盖率: {avg_integration:.3f}")
        print(f"  搜索相关性: {avg_relevance:.3f}")
        print(f"  跨域整合能力: {avg_cross_domain:.3f}")
        
        # 场景3评估 - 长期持久化
        print(f"场景3 - 长期记忆持久化:")
        print(f"  检索一致性: {scenario3_result['retrieval_consistency']:.3f}")
        print(f"  记忆质量: {scenario3_result['persistence_quality']:.3f}")
        
        # 整体评分
        overall_score = (
            (scenario1_result['avg_coherence'] + scenario1_result['avg_retrieval_accuracy']) / 2 * 0.4 +
            (avg_integration + avg_relevance + avg_cross_domain) / 3 * 0.4 +
            (scenario3_result['retrieval_consistency'] + scenario3_result['persistence_quality']) / 2 * 0.2
        )
        
        print(f"\n🎯 复杂场景整体评分: {overall_score:.3f}/1.0")
        
        if overall_score >= 0.7:
            print("✅ 记忆系统在复杂多步骤任务中表现优秀")
        elif overall_score >= 0.5:
            print("⚠️ 记忆系统表现良好，但复杂场景下仍有改进空间")
        else:
            print("❌ 记忆系统在复杂场景下需要显著改进")
        
        return {
            "overall_score": overall_score,
            "total_memories": total_memories,
            "scenario1": scenario1_result,
            "scenario2": scenario2_result,
            "scenario3": scenario3_result,
            "performance_metrics": {
                "step_coherence": scenario1_result['avg_coherence'],
                "retrieval_accuracy": scenario1_result['avg_retrieval_accuracy'],
                "domain_integration": avg_integration,
                "search_relevance": avg_relevance,
                "cross_domain_capability": avg_cross_domain,
                "persistence_consistency": scenario3_result['retrieval_consistency'],
                "memory_quality": scenario3_result['persistence_quality']
            }
        }

async def main():
    """主测试函数"""
    tester = ComplexScenarioTester(Path("/root/code/claude-memory-test"))
    
    try:
        results = await tester.run_comprehensive_complex_test()
        
        # 存储测试结果
        results_file = Path("/root/code/claude-memory-test/complex_scenarios_test_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n📁 详细测试结果已保存到: {results_file}")
        
        # 将测试经验存储到记忆系统
        tester.memory.remember(
            content=f"""
复杂多步骤任务记忆管理测试完成总结：

测试场景：
1. 多步骤Web应用开发 - 测试步骤间记忆连贯性和跨步骤检索
2. 知识领域整合应用 - 测试跨领域记忆整合和关联能力  
3. 长期记忆持久化 - 测试记忆质量和检索一致性

关键发现：
- 步骤连贯性评分: {results['performance_metrics']['step_coherence']:.3f}
- 跨步骤检索准确性: {results['performance_metrics']['retrieval_accuracy']:.3f}
- 领域整合能力: {results['performance_metrics']['domain_integration']:.3f}
- 搜索相关性: {results['performance_metrics']['search_relevance']:.3f}
- 跨域整合能力: {results['performance_metrics']['cross_domain_capability']:.3f}
- 长期一致性: {results['performance_metrics']['persistence_consistency']:.3f}

整体评分: {results['overall_score']:.3f}/1.0

结论：记忆系统在复杂多步骤任务中表现{'优秀' if results['overall_score'] >= 0.7 else '良好' if results['overall_score'] >= 0.5 else '需要改进'}，
能够有效支持多步骤工作流的记忆管理和知识整合。
            """,
            memory_type="episodic",
            title="复杂场景记忆管理测试总结",
            tags=["测试", "复杂场景", "多步骤任务", "记忆管理", "评估"],
            importance=9.0,
            scope="global"
        )
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())