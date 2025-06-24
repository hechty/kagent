#!/usr/bin/env python3
"""
长上下文和复杂场景下的记忆准确性测试
测试记忆系统在大量信息和复杂关联下的表现
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

class LongContextMemoryTester:
    """长上下文记忆测试器"""
    
    def __init__(self, project_path: Path):
        self.memory = MemoryManager(project_path=project_path)
        self.test_results = []
        self.memory_ids = []
        
    async def create_complex_knowledge_base(self):
        """创建复杂的知识库用于测试"""
        print("📚 创建复杂知识库...")
        
        # 大规模编程知识
        programming_topics = [
            {
                "title": "Python高级特性详解",
                "content": """
Python高级特性包括：
1. 装饰器(Decorators) - 函数增强器
   - @property：属性装饰器
   - @staticmethod：静态方法
   - @classmethod：类方法
   - 自定义装饰器：def decorator(func): return wrapper
2. 生成器(Generators) - 惰性计算
   - yield关键字：暂停函数执行
   - 生成器表达式：(x for x in range(10))
   - 协程：async def 和 await
3. 元编程(Metaprogramming)
   - __new__, __init__, __call__ 魔法方法
   - type()动态创建类
   - __getattr__, __setattr__ 属性访问控制
4. 上下文管理器(Context Managers)
   - with语句：资源管理
   - __enter__, __exit__ 协议
   - contextlib.contextmanager装饰器
                """,
                "tags": ["python", "高级特性", "装饰器", "生成器", "元编程"],
                "importance": 9.0
            },
            {
                "title": "分布式系统设计原理",
                "content": """
分布式系统核心概念：
1. CAP定理 - 一致性、可用性、分区容错性不可兼得
   - Consistency：所有节点数据一致
   - Availability：系统持续可用
   - Partition Tolerance：网络分区容错
2. 分布式一致性算法
   - Raft算法：Leader选举、日志复制
   - PBFT：拜占庭容错
   - Gossip协议：最终一致性
3. 分布式事务
   - 2PC：两阶段提交
   - 3PC：三阶段提交  
   - Saga模式：长事务处理
4. 微服务架构模式
   - 服务拆分策略
   - API网关模式
   - 服务发现与注册
   - 熔断器模式
                """,
                "tags": ["分布式系统", "CAP定理", "一致性", "微服务", "架构设计"],
                "importance": 9.5
            },
            {
                "title": "机器学习算法实现细节",
                "content": """
机器学习核心算法：
1. 监督学习算法
   - 线性回归：梯度下降优化
   - 逻辑回归：sigmoid函数、最大似然估计
   - 决策树：信息增益、基尼系数
   - 随机森林：Bagging集成
   - SVM：核技巧、软间隔
   - 神经网络：反向传播、梯度消失
2. 无监督学习
   - K-means聚类：质心更新
   - 层次聚类：单链接、完全链接
   - PCA：主成分分析、降维
   - t-SNE：非线性降维
3. 强化学习
   - Q-learning：值函数迭代
   - Policy Gradient：策略梯度
   - Actor-Critic：价值函数+策略函数
4. 深度学习
   - CNN：卷积、池化、全连接
   - RNN/LSTM：序列建模、长短期记忆
   - Transformer：注意力机制、自注意力
                """,
                "tags": ["机器学习", "深度学习", "算法", "神经网络", "强化学习"],
                "importance": 8.8
            },
            {
                "title": "数据库系统内核原理",
                "content": """
数据库系统核心组件：
1. 存储引擎
   - B+树索引：平衡多路搜索树
   - LSM树：Log-Structured Merge Tree
   - 页面管理：缓冲池、LRU替换
   - 事务日志：WAL预写日志
2. 查询优化器
   - 关系代数：选择、投影、连接
   - 查询计划：代价估计、统计信息
   - 连接算法：嵌套循环、排序合并、哈希连接
3. 并发控制
   - 锁机制：共享锁、排他锁、意向锁
   - MVCC：多版本并发控制
   - 死锁检测：等待图算法
4. 分布式数据库
   - 分片策略：水平分片、垂直分片
   - 副本一致性：主从复制、多主复制
   - 分布式事务：两阶段提交
                """,
                "tags": ["数据库", "存储引擎", "查询优化", "并发控制", "分布式"],
                "importance": 9.2
            },
            {
                "title": "容器化与云原生架构",
                "content": """
容器化技术栈：
1. Docker容器技术
   - 镜像层次结构：Union FS
   - 容器运行时：containerd、runc
   - 网络模式：bridge、host、overlay
   - 存储驱动：overlay2、devicemapper
2. Kubernetes编排
   - Pod：最小调度单元
   - Service：服务发现与负载均衡  
   - Deployment：应用部署管理
   - ConfigMap/Secret：配置管理
   - Ingress：流量入口管理
3. 服务网格
   - Istio：流量管理、安全、可观测性
   - Envoy代理：L7负载均衡
   - mTLS：双向认证
4. 云原生存储
   - CSI：容器存储接口
   - 持久卷：PV/PVC
   - StorageClass：动态供应
                """,
                "tags": ["docker", "kubernetes", "云原生", "容器", "微服务"],
                "importance": 8.5
            }
        ]
        
        # 存储复杂编程解决方案
        complex_solutions = [
            {
                "title": "高并发系统性能优化实战",
                "content": """
项目背景：电商系统在双11期间出现严重性能瓶颈
问题现象：
- QPS从正常5000降到500
- 响应时间从50ms飙升到5秒
- 数据库连接池耗尽
- 内存使用率达到95%

解决方案：
1. 应用层优化
   - 引入Redis缓存：热点数据缓存命中率99%
   - 数据库连接池调优：从20增加到100
   - 异步处理：订单处理改为消息队列异步
   - JVM调优：G1垃圾收集器，堆内存32GB

2. 数据库优化
   - 慢查询优化：添加复合索引，查询时间从2s降到10ms
   - 读写分离：主从架构，读请求分流到从库
   - 分库分表：订单表按用户ID哈希分256张表

3. 架构优化
   - CDN加速：静态资源响应时间从200ms降到20ms
   - 负载均衡：Nginx七层负载，后端20台服务器
   - 限流降级：令牌桶算法，保护核心业务

优化结果：
- QPS提升到15000，超出预期3倍
- 平均响应时间降到30ms
- 系统稳定性99.99%
- 双11期间零故障运行
                """,
                "tags": ["性能优化", "高并发", "缓存", "数据库优化", "架构设计"],
                "importance": 9.8
            },
            {
                "title": "分布式系统故障排查案例",
                "content": """
故障现象：
- 微服务间调用超时率突然飙升至30%
- 用户登录失败率增加
- 部分地区用户无法访问

排查过程：
1. 监控分析
   - Prometheus指标显示某个服务CPU使用率100%
   - Jaeger链路追踪发现auth-service调用缓慢
   - ELK日志显示大量连接超时错误

2. 根因分析
   - auth-service内存泄漏，频繁GC导致STW
   - Redis连接池配置错误，连接数不够
   - 网络延迟增加，可能是机房网络问题

3. 应急处理
   - 立即重启故障服务实例
   - 启用熔断器，避免雪崩效应
   - 临时扩容Redis连接池

4. 根本修复
   - 修复内存泄漏bug：StringBuilder重复使用导致
   - 优化Redis连接池配置
   - 增加服务健康检查和自动恢复

经验总结：
- 建立完善的监控告警体系
- 实施渐进式部署策略
- 设计容错和自恢复机制
- 定期进行故障演练
                """,
                "tags": ["故障排查", "分布式系统", "监控", "应急处理", "根因分析"],
                "importance": 9.5
            },
            {
                "title": "机器学习模型部署与监控",
                "content": """
项目需求：将推荐算法模型部署到生产环境
技术选型：TensorFlow Serving + Kubernetes + Prometheus

部署架构：
1. 模型服务化
   - TensorFlow SavedModel格式
   - gRPC/REST API接口
   - 模型版本管理
   - A/B测试支持

2. 容器化部署
   - Docker镜像构建优化：多阶段构建，镜像大小从2GB降到500MB
   - Kubernetes HPA：根据CPU/内存自动扩缩容
   - 资源限制：CPU 2核，内存4GB

3. 监控体系
   - 模型性能指标：预测延迟、QPS、错误率
   - 业务指标：CTR、转化率、用户满意度
   - 数据漂移检测：特征分布变化监控

4. 持续优化
   - 模型重训练：每周基于新数据重新训练
   - 超参数调优：使用Optuna自动调参
   - 特征工程：新增用户行为特征，CTR提升15%

部署结果：
- 模型推理延迟<50ms
- 日处理请求量1000万+
- 系统可用性99.9%
- 推荐效果CTR提升25%
                """,
                "tags": ["机器学习", "模型部署", "kubernetes", "监控", "TensorFlow"],
                "importance": 8.7
            }
        ]
        
        # 存储复杂工具脚本
        complex_tools = [
            {
                "title": "分布式日志收集分析工具",
                "content": """
import asyncio
import aiohttp
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
from collections import defaultdict, Counter

class DistributedLogAnalyzer:
    \"\"\"分布式系统日志收集和分析工具\"\"\"
    
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.log_patterns = {
            'error': re.compile(r'ERROR\\s+(.+)'),
            'warning': re.compile(r'WARN\\s+(.+)'),
            'api_call': re.compile(r'API\\s+(\\w+)\\s+/([^\\s]+)\\s+(\\d+)ms'),
            'sql_query': re.compile(r'SQL\\s+Query:\\s+(.+)\\s+\\[(\\d+)ms\\]'),
            'memory': re.compile(r'Memory:\\s+(\\d+)MB\\s+/\\s+(\\d+)MB'),
        }
        
    def load_config(self, config_path: str) -> Dict:
        \"\"\"加载配置文件\"\"\"
        with open(config_path, 'r') as f:
            return json.load(f)
    
    async def collect_logs_from_services(self, time_range: tuple) -> Dict[str, List]:
        \"\"\"从多个服务收集日志\"\"\"
        start_time, end_time = time_range
        all_logs = defaultdict(list)
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for service in self.config['services']:
                task = self.fetch_service_logs(session, service, start_time, end_time)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            for service_name, logs in results:
                all_logs[service_name] = logs
                
        return dict(all_logs)
    
    async def fetch_service_logs(self, session, service: Dict, start_time: str, end_time: str):
        \"\"\"获取单个服务的日志\"\"\"
        url = f"{service['log_endpoint']}/logs"
        params = {
            'start': start_time,
            'end': end_time,
            'level': 'all'
        }
        
        try:
            async with session.get(url, params=params) as response:
                logs = await response.json()
                return service['name'], logs
        except Exception as e:
            print(f"Failed to fetch logs from {service['name']}: {e}")
            return service['name'], []
    
    def analyze_performance_metrics(self, logs: Dict[str, List]) -> Dict:
        \"\"\"分析性能指标\"\"\"
        metrics = {
            'api_performance': defaultdict(list),
            'sql_performance': defaultdict(list),
            'error_frequency': defaultdict(int),
            'memory_usage': defaultdict(list),
            'service_health': {}
        }
        
        for service_name, service_logs in logs.items():
            for log_entry in service_logs:
                message = log_entry.get('message', '')
                timestamp = log_entry.get('timestamp')
                
                # API调用性能分析
                api_match = self.log_patterns['api_call'].search(message)
                if api_match:
                    method, endpoint, duration = api_match.groups()
                    metrics['api_performance'][f"{method} /{endpoint}"].append(int(duration))
                
                # SQL查询性能分析
                sql_match = self.log_patterns['sql_query'].search(message)
                if sql_match:
                    query, duration = sql_match.groups()
                    metrics['sql_performance'][query[:50]].append(int(duration))
                
                # 错误频率统计
                if self.log_patterns['error'].search(message):
                    error_type = self.extract_error_type(message)
                    metrics['error_frequency'][error_type] += 1
                
                # 内存使用情况
                memory_match = self.log_patterns['memory'].search(message)
                if memory_match:
                    used, total = memory_match.groups()
                    metrics['memory_usage'][service_name].append({
                        'timestamp': timestamp,
                        'used': int(used),
                        'total': int(total),
                        'usage_percent': int(used) / int(total) * 100
                    })
        
        return self.calculate_performance_statistics(metrics)
    
    def calculate_performance_statistics(self, metrics: Dict) -> Dict:
        \"\"\"计算性能统计信息\"\"\"
        stats = {}
        
        # API性能统计
        api_stats = {}
        for endpoint, durations in metrics['api_performance'].items():
            if durations:
                api_stats[endpoint] = {
                    'avg': np.mean(durations),
                    'p95': np.percentile(durations, 95),
                    'p99': np.percentile(durations, 99),
                    'max': max(durations),
                    'count': len(durations)
                }
        stats['api_performance'] = api_stats
        
        # SQL性能统计
        sql_stats = {}
        for query, durations in metrics['sql_performance'].items():
            if durations:
                sql_stats[query] = {
                    'avg': np.mean(durations),
                    'p95': np.percentile(durations, 95),
                    'count': len(durations)
                }
        stats['sql_performance'] = sql_stats
        
        # 错误统计
        stats['error_summary'] = dict(metrics['error_frequency'])
        
        # 内存使用统计
        memory_stats = {}
        for service, usage_data in metrics['memory_usage'].items():
            if usage_data:
                usage_percents = [data['usage_percent'] for data in usage_data]
                memory_stats[service] = {
                    'avg_usage': np.mean(usage_percents),
                    'max_usage': max(usage_percents),
                    'trend': self.calculate_trend(usage_data)
                }
        stats['memory_usage'] = memory_stats
        
        return stats
    
    def extract_error_type(self, message: str) -> str:
        \"\"\"提取错误类型\"\"\"
        common_errors = [
            'NullPointerException', 'SQLException', 'TimeoutException',
            'ConnectionException', 'ValidationException', 'AuthenticationException'
        ]
        
        for error_type in common_errors:
            if error_type in message:
                return error_type
        
        return 'Unknown Error'
    
    def calculate_trend(self, usage_data: List[Dict]) -> str:
        \"\"\"计算使用趋势\"\"\"
        if len(usage_data) < 2:
            return 'insufficient_data'
        
        values = [data['usage_percent'] for data in usage_data]
        first_half = np.mean(values[:len(values)//2])
        second_half = np.mean(values[len(values)//2:])
        
        if second_half > first_half * 1.1:
            return 'increasing'
        elif second_half < first_half * 0.9:
            return 'decreasing'
        else:
            return 'stable'
    
    def generate_report(self, analysis_results: Dict) -> str:
        \"\"\"生成分析报告\"\"\"
        report = []
        report.append("=== 分布式系统日志分析报告 ===\\n")
        
        # API性能报告
        report.append("API性能分析:")
        api_perf = analysis_results.get('api_performance', {})
        for endpoint, stats in sorted(api_perf.items(), key=lambda x: x[1]['p95'], reverse=True)[:10]:
            report.append(f"  {endpoint}:")
            report.append(f"    平均响应时间: {stats['avg']:.1f}ms")
            report.append(f"    P95响应时间: {stats['p95']:.1f}ms")
            report.append(f"    请求次数: {stats['count']}")
        
        # 错误统计报告
        report.append("\\n错误统计:")
        error_summary = analysis_results.get('error_summary', {})
        for error_type, count in sorted(error_summary.items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {error_type}: {count} 次")
        
        # 内存使用报告
        report.append("\\n内存使用情况:")
        memory_usage = analysis_results.get('memory_usage', {})
        for service, stats in memory_usage.items():
            report.append(f"  {service}:")
            report.append(f"    平均使用率: {stats['avg_usage']:.1f}%")
            report.append(f"    最高使用率: {stats['max_usage']:.1f}%")
            report.append(f"    使用趋势: {stats['trend']}")
        
        return "\\n".join(report)

# 使用示例
async def analyze_distributed_logs():
    analyzer = DistributedLogAnalyzer('${config_file}')
    
    # 分析最近1小时的日志
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)
    
    # 收集日志
    logs = await analyzer.collect_logs_from_services((
        start_time.isoformat(),
        end_time.isoformat()
    ))
    
    # 分析性能
    analysis = analyzer.analyze_performance_metrics(logs)
    
    # 生成报告
    report = analyzer.generate_report(analysis)
    print(report)
    
    return analysis

if __name__ == "__main__":
    result = asyncio.run(analyze_distributed_logs())
                """,
                "tags": ["日志分析", "分布式系统", "性能监控", "异步编程", "数据分析"],
                "importance": 9.0
            }
        ]
        
        # 存储所有记忆
        stored_memories = []
        
        # 存储编程知识
        for topic in programming_topics:
            memory_id = self.memory.remember(
                content=topic["content"],
                memory_type="semantic",
                title=topic["title"],
                tags=topic["tags"],
                importance=topic["importance"],
                scope="global"
            )
            stored_memories.append(("knowledge", topic["title"], memory_id))
            self.memory_ids.append(memory_id)
        
        # 存储解决方案经验
        for solution in complex_solutions:
            memory_id = self.memory.remember(
                content=solution["content"],
                memory_type="episodic",
                title=solution["title"],
                tags=solution["tags"],
                importance=solution["importance"],
                scope="project"
            )
            stored_memories.append(("solution", solution["title"], memory_id))
            self.memory_ids.append(memory_id)
        
        # 存储工具能力
        for tool in complex_tools:
            memory_id = self.memory.remember(
                content=tool["content"],
                memory_type="procedural",
                title=tool["title"],
                tags=tool["tags"],
                importance=tool["importance"],  
                scope="global"
            )
            stored_memories.append(("tool", tool["title"], memory_id))
            self.memory_ids.append(memory_id)
        
        print(f"✅ 成功创建复杂知识库，共存储 {len(stored_memories)} 个记忆")
        return stored_memories
    
    async def test_cross_domain_recall_accuracy(self):
        """测试跨领域记忆召回准确性"""
        print("\n🔍 测试跨领域记忆召回准确性")
        print("-" * 50)
        
        # 复杂查询测试用例
        test_queries = [
            {
                "query": "Python装饰器在微服务架构中的应用",
                "expected_domains": ["python", "微服务", "装饰器"],
                "min_results": 2
            },
            {
                "query": "分布式系统性能优化和监控",
                "expected_domains": ["分布式系统", "性能优化", "监控"],
                "min_results": 3
            },
            {
                "query": "机器学习模型部署的数据库连接池优化",
                "expected_domains": ["机器学习", "数据库", "部署"],
                "min_results": 2
            },
            {
                "query": "容器化环境下的日志分析和故障排查",
                "expected_domains": ["容器", "日志分析", "故障排查"],
                "min_results": 2
            },
            {
                "query": "高并发场景下的缓存策略和一致性保证",
                "expected_domains": ["高并发", "缓存", "一致性"],
                "min_results": 2
            }
        ]
        
        accuracy_results = []
        
        for i, test_case in enumerate(test_queries, 1):
            print(f"\n测试用例 {i}: {test_case['query']}")
            
            start_time = time.time()
            results = self.memory.recall(test_case["query"], max_results=10)
            recall_time = time.time() - start_time
            
            print(f"召回时间: {recall_time:.3f}秒")
            print(f"找到结果: {len(results)} 个")
            
            # 分析召回准确性
            relevant_count = 0
            domain_coverage = set()
            
            for result in results:
                print(f"  - {result.memory.title} (相关性: {result.relevance_score:.3f})")
                print(f"    标签: {result.memory.tags}")
                
                # 检查领域覆盖
                for expected_domain in test_case["expected_domains"]:
                    if any(expected_domain.lower() in tag.lower() for tag in result.memory.tags):
                        domain_coverage.add(expected_domain)
                
                # 相关性阈值判断
                if result.relevance_score > 0.3:
                    relevant_count += 1
            
            # 计算准确性指标
            precision = relevant_count / len(results) if results else 0
            domain_coverage_rate = len(domain_coverage) / len(test_case["expected_domains"])
            meets_min_results = len(results) >= test_case["min_results"]
            
            accuracy_score = (precision + domain_coverage_rate + (1 if meets_min_results else 0)) / 3
            
            accuracy_results.append({
                "query": test_case["query"],
                "results_count": len(results),
                "relevant_count": relevant_count,
                "precision": precision,
                "domain_coverage_rate": domain_coverage_rate,
                "accuracy_score": accuracy_score,
                "recall_time": recall_time
            })
            
            print(f"  准确性评分: {accuracy_score:.3f}")
        
        # 整体准确性统计
        avg_accuracy = sum(r["accuracy_score"] for r in accuracy_results) / len(accuracy_results)
        avg_recall_time = sum(r["recall_time"] for r in accuracy_results) / len(accuracy_results)
        
        print(f"\n📊 跨领域召回准确性测试结果:")
        print(f"平均准确性: {avg_accuracy:.3f}")
        print(f"平均召回时间: {avg_recall_time:.3f}秒")
        
        return accuracy_results
    
    async def test_long_context_memory_coherence(self):
        """测试长上下文记忆连贯性"""
        print("\n🧠 测试长上下文记忆连贯性")
        print("-" * 50)
        
        # 模拟长期使用场景
        long_context_scenarios = [
            {
                "context": "正在开发一个电商推荐系统",
                "questions": [
                    "机器学习推荐算法有哪些",
                    "如何部署机器学习模型到生产环境",
                    "高并发推荐服务的性能优化",
                    "推荐系统的A/B测试和监控"
                ]
            },
            {
                "context": "构建分布式微服务架构",
                "questions": [
                    "微服务拆分的最佳实践",
                    "服务间通信和数据一致性",
                    "容器化部署和编排",
                    "分布式系统的监控和故障处理"
                ]
            }
        ]
        
        coherence_results = []
        
        for scenario in long_context_scenarios:
            print(f"\n场景: {scenario['context']}")
            scenario_memories = []
            context_keywords = set()
            
            for i, question in enumerate(scenario["questions"], 1):
                print(f"\n第{i}步: {question}")
                
                # 构建上下文增强的查询
                if scenario_memories:
                    context_tags = []
                    for mem in scenario_memories[-2:]:  # 使用最近2个记忆作为上下文
                        context_tags.extend(mem.memory.tags)
                    enhanced_query = f"{question} {' '.join(set(context_tags))}"
                else:
                    enhanced_query = question
                
                results = self.memory.recall(enhanced_query, max_results=5)
                
                if results:
                    best_result = results[0]
                    scenario_memories.append(best_result)
                    context_keywords.update(best_result.memory.tags)
                    
                    print(f"  最佳匹配: {best_result.memory.title}")
                    print(f"  相关性: {best_result.relevance_score:.3f}")
                    print(f"  记忆类型: {best_result.memory.memory_type.value}")
                
                # 检查上下文连贯性
                if i > 1:
                    prev_tags = set(scenario_memories[-2].memory.tags)
                    curr_tags = set(scenario_memories[-1].memory.tags)
                    tag_overlap = len(prev_tags & curr_tags)
                    coherence_score = tag_overlap / len(prev_tags | curr_tags) if prev_tags | curr_tags else 0
                    print(f"  上下文连贯性: {coherence_score:.3f}")
            
            # 分析整个场景的记忆连贯性
            if len(scenario_memories) > 1:
                # 计算记忆间的语义相似性
                semantic_scores = []
                for i in range(len(scenario_memories) - 1):
                    tags1 = set(scenario_memories[i].memory.tags)
                    tags2 = set(scenario_memories[i+1].memory.tags)
                    similarity = len(tags1 & tags2) / len(tags1 | tags2) if tags1 | tags2 else 0
                    semantic_scores.append(similarity)
                
                avg_coherence = sum(semantic_scores) / len(semantic_scores) if semantic_scores else 0
                
                coherence_results.append({
                    "scenario": scenario["context"],
                    "memory_count": len(scenario_memories),
                    "avg_coherence": avg_coherence,
                    "context_coverage": len(context_keywords)
                })
                
                print(f"\n场景连贯性评分: {avg_coherence:.3f}")
        
        return coherence_results
    
    async def test_memory_interference_and_noise(self):
        """测试记忆干扰和噪声处理"""
        print("\n🎯 测试记忆干扰和噪声处理")
        print("-" * 50)
        
        # 添加干扰记忆
        noise_memories = [
            "今天天气很好，适合出去散步。阳光明媚，微风习习。",
            "午餐吃了意大利面，味道不错。餐厅环境也很舒适。",
            "看了一部科幻电影，特效很棒。故事情节也很吸引人。",
            "学习了一些历史知识，了解了古代文明的发展。",
            "听了一场音乐会，演奏者技艺高超。",
        ]
        
        # 存储噪声记忆
        noise_ids = []
        for i, noise in enumerate(noise_memories):
            memory_id = self.memory.remember(
                content=noise,
                memory_type="working",
                title=f"日常记录{i+1}",
                tags=["日常", "生活"],
                importance=2.0,
                scope="project"
            )
            noise_ids.append(memory_id)
        
        print(f"添加了 {len(noise_ids)} 个噪声记忆")
        
        # 测试抗干扰能力
        interference_tests = [
            {
                "query": "Python异步编程协程",
                "expected_type": "semantic",
                "expected_tags": ["python", "异步编程"]
            },
            {
                "query": "分布式系统一致性算法",
                "expected_type": "semantic", 
                "expected_tags": ["分布式系统", "一致性"]
            },
            {
                "query": "机器学习模型部署优化",
                "expected_type": "episodic",
                "expected_tags": ["机器学习", "部署"]
            }
        ]
        
        interference_results = []
        
        for test in interference_tests:
            print(f"\n测试查询: {test['query']}")
            
            results = self.memory.recall(test["query"], max_results=10)
            
            # 分析结果质量
            relevant_results = []
            noise_results = []
            
            for result in results:
                is_noise = any(tag in ["日常", "生活"] for tag in result.memory.tags)
                if is_noise:
                    noise_results.append(result)
                else:
                    # 检查是否与预期相关
                    is_relevant = any(
                        expected_tag.lower() in tag.lower() 
                        for tag in result.memory.tags 
                        for expected_tag in test["expected_tags"]
                    )
                    if is_relevant:
                        relevant_results.append(result)
            
            noise_ratio = len(noise_results) / len(results) if results else 0
            relevance_ratio = len(relevant_results) / len(results) if results else 0
            
            print(f"  总结果数: {len(results)}")
            print(f"  相关结果: {len(relevant_results)} ({relevance_ratio:.1%})")
            print(f"  噪声结果: {len(noise_results)} ({noise_ratio:.1%})")
            
            # 抗干扰评分 (噪声比例越低越好)
            anti_interference_score = max(0, 1 - noise_ratio)
            
            interference_results.append({
                "query": test["query"],
                "total_results": len(results),
                "relevant_results": len(relevant_results),
                "noise_results": len(noise_results),
                "relevance_ratio": relevance_ratio,
                "noise_ratio": noise_ratio,
                "anti_interference_score": anti_interference_score
            })
            
            print(f"  抗干扰评分: {anti_interference_score:.3f}")
        
        # 清理噪声记忆
        for noise_id in noise_ids:
            # 这里应该有删除记忆的方法，但当前实现中没有
            pass
        
        return interference_results
    
    async def run_comprehensive_accuracy_test(self):
        """运行综合准确性测试"""
        print("🧪 开始长上下文复杂场景记忆准确性测试")
        print("=" * 60)
        
        # 1. 创建复杂知识库
        stored_memories = await self.create_complex_knowledge_base()
        
        # 2. 测试跨领域召回准确性
        cross_domain_results = await self.test_cross_domain_recall_accuracy()
        
        # 3. 测试长上下文连贯性
        coherence_results = await self.test_long_context_memory_coherence()
        
        # 4. 测试抗干扰能力
        interference_results = await self.test_memory_interference_and_noise()
        
        # 5. 综合评估
        print("\n📊 综合测试结果评估")
        print("=" * 50)
        
        # 跨领域召回评估
        avg_cross_domain_accuracy = sum(r["accuracy_score"] for r in cross_domain_results) / len(cross_domain_results)
        print(f"跨领域召回准确性: {avg_cross_domain_accuracy:.3f}")
        
        # 上下文连贯性评估
        if coherence_results:
            avg_coherence = sum(r["avg_coherence"] for r in coherence_results) / len(coherence_results)
            print(f"长上下文连贯性: {avg_coherence:.3f}")
        
        # 抗干扰能力评估
        avg_anti_interference = sum(r["anti_interference_score"] for r in interference_results) / len(interference_results)
        print(f"抗干扰能力: {avg_anti_interference:.3f}")
        
        # 整体准确性评分
        overall_accuracy = (avg_cross_domain_accuracy + (avg_coherence if coherence_results else 0.5) + avg_anti_interference) / 3
        print(f"\n🎯 整体记忆准确性评分: {overall_accuracy:.3f}/1.0")
        
        if overall_accuracy >= 0.8:
            print("✅ 记忆系统在长上下文复杂场景下表现优秀")
        elif overall_accuracy >= 0.6:
            print("⚠️ 记忆系统表现良好，但仍有优化空间")
        else:
            print("❌ 记忆系统需要显著改进")
        
        return {
            "overall_accuracy": overall_accuracy,
            "cross_domain_accuracy": avg_cross_domain_accuracy,
            "context_coherence": avg_coherence if coherence_results else 0,
            "anti_interference": avg_anti_interference,
            "stored_memories_count": len(stored_memories),
            "test_details": {
                "cross_domain": cross_domain_results,
                "coherence": coherence_results,
                "interference": interference_results
            }
        }

async def main():
    """主测试函数"""
    tester = LongContextMemoryTester(Path("/root/code/claude-memory-test"))
    
    try:
        results = await tester.run_comprehensive_accuracy_test()
        
        # 存储测试结果
        results_file = Path("/root/code/claude-memory-test/long_context_test_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n📁 详细测试结果已保存到: {results_file}")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())