#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置模块
"""

import os
import logging

# 尝试从config导入日志级别配置，如果失败则使用默认值
try:
    from config import LOG_LEVEL_CONSOLE, LOG_LEVEL_FILE
except ImportError:
    # 如果config.py不存在或没有配置，使用默认值
    LOG_LEVEL_CONSOLE = "INFO"
    LOG_LEVEL_FILE = "DEBUG"

# 日志级别映射
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# 全局统一的日志文件名
UNIFIED_LOG_FILE = "resume_filter.log"

# 全局文件handler（所有logger共享）
_file_handler = None


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # 添加颜色
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def _get_log_level(level_name: str) -> int:
    """
    将字符串日志级别转换为logging级别
    
    Args:
        level_name: 日志级别名称（如 "INFO", "DEBUG"）
        
    Returns:
        logging级别常量
    """
    return LOG_LEVELS.get(level_name.upper(), logging.INFO)


def _get_global_file_handler():
    """获取全局共享的文件handler"""
    global _file_handler
    
    if _file_handler is None:
        # 创建日志目录
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_path = os.path.join(log_dir, UNIFIED_LOG_FILE)
        
        # 创建文件handler（使用配置的日志级别）
        _file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_log_level = _get_log_level(LOG_LEVEL_FILE)
        _file_handler.setLevel(file_log_level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        _file_handler.setFormatter(file_formatter)
    
    return _file_handler


def setup_logger(name: str = "app"):
    """
    设置日志系统（所有日志统一输出到一个文件）
    
    Args:
        name: logger名称（用于标识不同模块，日志中会显示模块名称）
    
    注意：
        所有模块的日志都会统一输出到 logs/resume_filter.log 文件
        日志级别可通过 config.py 中的 LOG_LEVEL_CONSOLE 和 LOG_LEVEL_FILE 配置
    """
    logger = logging.getLogger(name)
    # logger本身的级别设为最低（DEBUG），由handler控制实际输出级别
    logger.setLevel(logging.DEBUG)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 使用全局共享的文件handler（使用配置的日志级别）
    file_handler = _get_global_file_handler()
    logger.addHandler(file_handler)
    
    # 控制台handler（带颜色，每个logger独立，使用配置的日志级别）
    console_handler = logging.StreamHandler()
    console_log_level = _get_log_level(LOG_LEVEL_CONSOLE)
    console_handler.setLevel(console_log_level)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger
