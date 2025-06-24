#!/bin/bash
# 设置记忆工具为全局命令
# 让记忆工具使用起来就像原生工具一样简洁

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 设置记忆工具为全局命令${NC}"
echo "=================================="

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 检查记忆命令文件
COMMANDS=("memory-recall" "memory-remember" "memory-status")
for cmd in "${COMMANDS[@]}"; do
    if [[ ! -f "$SCRIPT_DIR/$cmd" ]]; then
        echo -e "${RED}❌ 错误: 找不到命令文件 $cmd${NC}"
        exit 1
    fi
done

# 测试记忆系统
echo -e "${BLUE}🧪 测试记忆系统...${NC}"
cd "$SCRIPT_DIR/claude-memory-system"
source .venv/bin/activate

python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from claude_memory import MemoryManager
    from pathlib import Path
    memory = MemoryManager(Path('..'))
    print('✅ 记忆系统正常')
except Exception as e:
    print(f'❌ 记忆系统异常: {e}')
    exit(1)
"

if [[ $? -ne 0 ]]; then
    echo -e "${RED}❌ 记忆系统测试失败${NC}"
    exit 1
fi

cd "$SCRIPT_DIR"

# 创建符号链接到 /usr/local/bin (需要sudo)
echo -e "${BLUE}🔗 创建全局命令链接...${NC}"

BIN_DIR="/usr/local/bin"
if [[ ! -d "$BIN_DIR" ]]; then
    echo -e "${YELLOW}⚠️ 目录 $BIN_DIR 不存在，尝试创建...${NC}"
    sudo mkdir -p "$BIN_DIR"
fi

for cmd in "${COMMANDS[@]}"; do
    echo -e "${YELLOW}链接 $cmd -> $BIN_DIR/$cmd${NC}"
    sudo ln -sf "$SCRIPT_DIR/$cmd" "$BIN_DIR/$cmd"
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ $cmd 链接成功${NC}"
    else
        echo -e "${RED}❌ $cmd 链接失败${NC}"
        exit 1
    fi
done

# 验证命令可用性
echo -e "${BLUE}🧪 验证全局命令...${NC}"
for cmd in "${COMMANDS[@]}"; do
    if command -v "$cmd" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $cmd 命令可用${NC}"
    else
        echo -e "${RED}❌ $cmd 命令不可用${NC}"
        exit 1
    fi
done

# 测试命令
echo -e "${BLUE}🎯 测试命令功能...${NC}"

echo -e "${YELLOW}测试 memory-status:${NC}"
memory-status

echo -e "${YELLOW}测试 memory-remember:${NC}"
memory-remember "全局命令测试" "这是全局命令功能测试" semantic 6.0 测试 全局

echo -e "${YELLOW}测试 memory-recall:${NC}"
memory-recall "全局命令" 2

echo ""
echo -e "${GREEN}🎉 记忆工具全局命令设置完成!${NC}"
echo ""
echo -e "${BLUE}📖 使用方法 (现在可以在任何地方使用):${NC}"
echo ""
echo -e "${GREEN}1. 搜索记忆:${NC}"
echo -e "${YELLOW}   memory-recall \"Python性能优化\"${NC}"
echo -e "${YELLOW}   memory-recall \"搜索词\" 5 0.2${NC}"
echo ""
echo -e "${GREEN}2. 保存记忆:${NC}"
echo -e "${YELLOW}   memory-remember \"标题\" \"内容\"${NC}"
echo -e "${YELLOW}   memory-remember \"标题\" \"内容\" semantic 8.0 标签1 标签2${NC}"
echo ""
echo -e "${GREEN}3. 查看状态:${NC}"
echo -e "${YELLOW}   memory-status${NC}"
echo ""
echo -e "${BLUE}🎯 现在在Claude Code中可以直接使用Bash工具调用:${NC}"
echo -e "${GREEN}   Bash: memory-recall \"问题关键词\"${NC}"
echo -e "${GREEN}   Bash: memory-remember \"标题\" \"内容\"${NC}"
echo -e "${GREEN}   Bash: memory-status${NC}"
echo ""
echo -e "${GREEN}✨ 记忆工具现在就像Bash、Read、Write一样简洁易用了!${NC}"