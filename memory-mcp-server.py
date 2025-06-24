#!/usr/bin/env python3
"""
Claude Code 记忆系统 MCP 服务器
提供简洁的记忆工具API，无需关心底层实现细节
"""

import asyncio
import json
import sys
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

# 添加记忆系统路径
sys.path.insert(0, str(Path(__file__).parent / "claude-memory-system"))

try:
    from claude_memory import MemoryManager
    from claude_memory.models.memory import MemoryType
except ImportError as e:
    print(f"Error importing memory system: {e}", file=sys.stderr)
    sys.exit(1)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MemoryMCPServer:
    """记忆系统MCP服务器"""
    
    def __init__(self):
        self.memory_manager = None
        self.project_path = Path("/root/code")
        
    def initialize_memory(self):
        """初始化记忆管理器"""
        try:
            if not self.memory_manager:
                self.memory_manager = MemoryManager(self.project_path)
                # 唤醒记忆系统
                snapshot = self.memory_manager.awaken("MCP服务器启动")
                logger.info(f"记忆系统已初始化，共{snapshot.memory_statistics.total_memories}个记忆")
        except Exception as e:
            logger.error(f"记忆系统初始化失败: {e}")
            raise
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "tools/list":
                return self.list_tools()
            elif method == "tools/call":
                return self.call_tool(params)
            else:
                return {
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            logger.error(f"处理请求失败: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def list_tools(self) -> Dict[str, Any]:
        """列出可用工具"""
        return {
            "tools": [
                {
                    "name": "memory_recall",
                    "description": "搜索相关记忆内容",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索关键词或问题描述"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "最大返回结果数",
                                "default": 3
                            },
                            "min_relevance": {
                                "type": "number",
                                "description": "最小相关性阈值 (0-1)",
                                "default": 0.1
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "memory_remember",
                    "description": "记录新的记忆内容",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "要记录的详细内容"
                            },
                            "title": {
                                "type": "string",
                                "description": "记忆标题"
                            },
                            "memory_type": {
                                "type": "string",
                                "enum": ["semantic", "episodic", "procedural", "working"],
                                "description": "记忆类型",
                                "default": "semantic"
                            },
                            "importance": {
                                "type": "number",
                                "description": "重要性评分 (1-10)",
                                "default": 5.0
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "相关标签",
                                "default": []
                            }
                        },
                        "required": ["content", "title"]
                    }
                },
                {
                    "name": "memory_status",
                    "description": "获取记忆系统状态",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            ]
        }
    
    def call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        # 确保记忆系统已初始化
        self.initialize_memory()
        
        if tool_name == "memory_recall":
            return self.tool_memory_recall(arguments)
        elif tool_name == "memory_remember":
            return self.tool_memory_remember(arguments)
        elif tool_name == "memory_status":
            return self.tool_memory_status(arguments)
        else:
            return {
                "error": {
                    "code": -32602,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
    
    def tool_memory_recall(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """搜索记忆工具"""
        try:
            query = args.get("query", "")
            max_results = args.get("max_results", 3)
            min_relevance = args.get("min_relevance", 0.1)
            
            if not query:
                return {
                    "error": {
                        "code": -32602,
                        "message": "Query parameter is required"
                    }
                }
            
            # 执行搜索
            results = self.memory_manager.recall(
                query=query,
                max_results=max_results,
                min_relevance=min_relevance
            )
            
            # 格式化结果
            formatted_results = []
            for memory in results:
                formatted_results.append({
                    "id": memory.id,
                    "title": memory.title,
                    "content": memory.content,
                    "memory_type": memory.memory_type.value,
                    "importance": memory.importance,
                    "tags": memory.tags,
                    "created_at": memory.created_at.isoformat(),
                    "relevance_score": getattr(memory, 'relevance_score', None)
                })
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"🔍 记忆搜索结果 (查询: '{query}'):\n\n" + 
                               (f"找到 {len(formatted_results)} 个相关记忆:\n\n" + 
                                "\n".join([
                                    f"📝 **{r['title']}**\n"
                                    f"   内容: {r['content'][:100]}{'...' if len(r['content']) > 100 else ''}\n"
                                    f"   类型: {r['memory_type']} | 重要性: {r['importance']}/10\n"
                                    f"   标签: {', '.join(r['tags']) if r['tags'] else '无'}\n"
                                    for r in formatted_results
                                ]) if formatted_results else "未找到相关记忆")
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"记忆搜索失败: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": f"Memory recall failed: {str(e)}"
                }
            }
    
    def tool_memory_remember(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """记录记忆工具"""
        try:
            content = args.get("content", "")
            title = args.get("title", "")
            memory_type = args.get("memory_type", "semantic")
            importance = args.get("importance", 5.0)
            tags = args.get("tags", [])
            
            if not content or not title:
                return {
                    "error": {
                        "code": -32602,
                        "message": "Content and title parameters are required"
                    }
                }
            
            # 记录记忆
            memory_id = self.memory_manager.remember(
                content=content,
                title=title,
                memory_type=MemoryType(memory_type),
                importance=importance,
                tags=tags
            )
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"✅ 记忆已成功保存!\n\n"
                               f"📝 标题: {title}\n"
                               f"📄 内容: {content[:100]}{'...' if len(content) > 100 else ''}\n"
                               f"🏷️ 类型: {memory_type}\n"
                               f"⭐ 重要性: {importance}/10\n"
                               f"🔖 标签: {', '.join(tags) if tags else '无'}\n"
                               f"🆔 记忆ID: {memory_id[:8]}..."
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"记忆保存失败: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": f"Memory save failed: {str(e)}"
                }
            }
    
    def tool_memory_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取记忆系统状态"""
        try:
            snapshot = self.memory_manager.awaken("状态查询")
            stats = snapshot.memory_statistics
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"🧠 记忆系统状态报告\n\n"
                               f"📊 总记忆数: {stats.total_memories}\n"
                               f"📈 各类型分布:\n"
                               f"   • 语义记忆: {stats.by_type.get('semantic', 0)}\n"
                               f"   • 事件记忆: {stats.by_type.get('episodic', 0)}\n"
                               f"   • 程序记忆: {stats.by_type.get('procedural', 0)}\n"
                               f"   • 工作记忆: {stats.by_type.get('working', 0)}\n"
                               f"⭐ 平均重要性: {stats.average_importance:.1f}/10\n"
                               f"🗂️ 活跃标签数: {len(stats.all_tags)}\n"
                               f"📁 存储路径: {self.project_path}\n"
                               f"✅ 系统状态: 正常运行"
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"状态查询失败: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": f"Status query failed: {str(e)}"
                }
            }

async def handle_stdio():
    """处理标准输入输出通信"""
    server = MemoryMCPServer()
    
    # 发送初始化消息
    init_response = {
        "jsonrpc": "2.0",
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "claude-memory-mcp-server",
                "version": "1.0.0"
            }
        }
    }
    
    while True:
        try:
            # 读取请求
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
                
            try:
                request = json.loads(line.strip())
            except json.JSONDecodeError:
                continue
            
            # 处理请求
            response = server.handle_request(request)
            
            # 构建完整响应
            full_response = {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": response if "error" not in response else None,
                "error": response.get("error") if "error" in response else None
            }
            
            # 发送响应
            print(json.dumps(full_response), flush=True)
            
        except Exception as e:
            logger.error(f"处理请求时发生错误: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    try:
        asyncio.run(handle_stdio())
    except KeyboardInterrupt:
        logger.info("MCP服务器已停止")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        sys.exit(1)