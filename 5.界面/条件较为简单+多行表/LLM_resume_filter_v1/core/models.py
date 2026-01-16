#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型定义
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class FilterResult:
    """筛选结果"""
    passed: bool  # 是否通过
    reason: str  # 原因说明
    source: str  # 来源：'rule' 或 'llm'
    details: Optional[Dict] = None  # 详细信息


@dataclass
class ScreeningResult:
    """筛选结果"""
    resume_id: str  # 简历序号
    job_id: int  # 岗位序号
    job_name: str  # 岗位名称
    passed: bool  # 是否通过
    filter_details: List[Dict]  # 各筛选条件的详细结果
    summary: str  # 总结说明
