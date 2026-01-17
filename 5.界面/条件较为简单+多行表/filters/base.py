#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础筛选器类
"""

from abc import ABC, abstractmethod
from typing import Dict
from core.models import FilterResult


class BaseFilter(ABC):
    """基础筛选器抽象类"""
    
    def __init__(self, model_manager=None, rule_matcher=None, llm_matcher=None):
        """
        初始化基础筛选器
        
        Args:
            model_manager: 模型管理器
            rule_matcher: 规则匹配器
            llm_matcher: LLM匹配器
        """
        self.model_manager = model_manager
        self.rule_matcher = rule_matcher
        self.llm_matcher = llm_matcher
    
    @abstractmethod
    async def filter(self, job_data: Dict, resume_data: Dict) -> FilterResult:
        """
        执行筛选
        
        Args:
            job_data: 岗位数据
            resume_data: 简历数据
        
        Returns:
            FilterResult
        """
        pass
