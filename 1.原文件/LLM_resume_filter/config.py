#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
"""

# LLM  配置
# LLM  服务地址
LLM_URL = "http://192.168.1.100:1234"
# LLM  模型名称
LLM_MODEL = "qwen/qwen3-4b-2507"

# 日志级别配置
# 可选值: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
# DEBUG: 显示所有日志（最详细）
# INFO: 显示信息、警告、错误和严重错误
# WARNING: 显示警告、错误和严重错误
# ERROR: 只显示错误和严重错误
# CRITICAL: 只显示严重错误
LOG_LEVEL_CONSOLE = "INFO"  # 控制台日志级别
LOG_LEVEL_FILE = "INFO"    # 文件日志级别（建议保持DEBUG以记录所有信息）

