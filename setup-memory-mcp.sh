#!/bin/bash
"""
Claude Code 记忆系统 MCP 工具注册脚本
一键设置简洁的记忆工具API
"""

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧠 Claude Code 记忆系统 MCP 工具设置${NC}"
echo "=" * 50

# 获取当前目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_SERVER_PATH="$SCRIPT_DIR/memory-mcp-server.py"

echo -e "${YELLOW}📍 当前目录: $SCRIPT_DIR${NC}"
echo -e "${YELLOW}🔧 MCP服务器路径: $MCP_SERVER_PATH${NC}"

# 检查MCP服务器文件
if [[ ! -f "$MCP_SERVER_PATH" ]]; then
    echo -e "${RED}❌ 错误: 找不到MCP服务器文件 $MCP_SERVER_PATH${NC}"
    exit 1
fi

# 检查记忆系统
echo -e "${BLUE}🔍 检查记忆系统...${NC}"
if [[ ! -d "$SCRIPT_DIR/claude-memory-system" ]]; then
    echo -e "${RED}❌ 错误: 找不到记忆系统目录${NC}"
    exit 1
fi

# 激活虚拟环境并测试记忆系统
cd "$SCRIPT_DIR/claude-memory-system"
source .venv/bin/activate

echo -e "${BLUE}🧪 测试记忆系统...${NC}"
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from claude_memory import MemoryManager
    from pathlib import Path
    memory = MemoryManager(Path('..'))
    print('✅ 记忆系统测试成功')
except Exception as e:
    print(f'❌ 记忆系统测试失败: {e}')
    exit(1)
"

if [[ $? -ne 0 ]]; then
    echo -e "${RED}❌ 记忆系统测试失败${NC}"
    exit 1
fi

cd "$SCRIPT_DIR"

# 注册MCP服务器
echo -e "${BLUE}📝 注册MCP服务器...${NC}"
echo -e "${YELLOW}执行命令: claude mcp add claude-memory $MCP_SERVER_PATH${NC}"

if claude mcp add claude-memory "$MCP_SERVER_PATH"; then
    echo -e "${GREEN}✅ MCP服务器注册成功!${NC}"
else
    echo -e "${RED}❌ MCP服务器注册失败${NC}"
    echo -e "${YELLOW}💡 请确保Claude Code已正确安装并可访问${NC}"
    exit 1
fi

# 列出已注册的MCP服务器
echo -e "${BLUE}📋 当前MCP服务器列表:${NC}"
claude mcp list

echo ""
echo -e "${GREEN}🎉 记忆系统MCP工具设置完成!${NC}"
echo ""
echo -e "${BLUE}🚀 使用方法:${NC}"
echo -e "${YELLOW}启动Claude Code后，您可以使用以下简洁命令:${NC}"
echo ""
echo -e "${GREEN}1. 搜索记忆:${NC}"
echo "   memory_recall(query=\"Python性能优化\")"
echo ""
echo -e "${GREEN}2. 记录记忆:${NC}"
echo "   memory_remember(content=\"内容\", title=\"标题\")"
echo ""
echo -e "${GREEN}3. 查看状态:${NC}"
echo "   memory_status()"
echo ""
echo -e "${BLUE}📖 详细参数说明:${NC}"
echo -e "${YELLOW}memory_recall:${NC}"
echo "   - query: 搜索关键词 (必需)"
echo "   - max_results: 最大结果数 (默认3)"
echo "   - min_relevance: 最小相关性 (默认0.1)"
echo ""
echo -e "${YELLOW}memory_remember:${NC}"
echo "   - content: 记忆内容 (必需)"
echo "   - title: 记忆标题 (必需)" 
echo "   - memory_type: semantic|episodic|procedural|working (默认semantic)"
echo "   - importance: 重要性1-10 (默认5.0)"
echo "   - tags: 标签列表 (默认[])"
echo ""
echo -e "${GREEN}✨ 现在您可以启动Claude Code并享受简洁的记忆工具API了!${NC}"