#!/bin/bash
# Wrapper script for MCP server to use uv run

cd /root/code/claude-memory-system
exec uv run python memory-mcp-server.py "$@"