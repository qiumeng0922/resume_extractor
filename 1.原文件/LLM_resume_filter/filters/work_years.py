#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作经验筛选器
"""

from typing import Dict
from core.models import FilterResult
from filters.base import BaseFilter
from matchers.llm_matcher import LLMMatcher


class WorkYearsFilter(BaseFilter):
    """工作经验筛选器"""
    
    async def filter(self, job_data: Dict, resume_data: Dict) -> FilterResult:
        """筛选：工作经验要求（使用LLM匹配，岗位职责和岗位任职条件的值就是工作经验要求）"""
        # 岗位职责和岗位任职条件的值本身就是工作经验要求，直接使用
        # 检查是否有岗位职责或岗位任职条件
        job_duty = job_data.get("岗位职责", [])
        job_requirement = job_data.get("岗位任职条件", [])
        
        if not job_duty and not job_requirement:
            return FilterResult(
                passed=True,
                reason="岗位未明确工作经验要求（无岗位职责和岗位任职条件）",
                source="rule"
            )
        
        # 使用LLM匹配（岗位职责和岗位任职条件作为工作经验要求，requirement参数不再使用）
        return await self.llm_matcher.match_work_years_llm(None, job_data, resume_data)
