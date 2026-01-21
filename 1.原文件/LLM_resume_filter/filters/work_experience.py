#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作经历筛选器
"""

from typing import Dict
from core.models import FilterResult
from filters.base import BaseFilter
from extractors.requirement_extractor import RequirementExtractor
from matchers.llm_matcher import LLMMatcher


class WorkExperienceFilter(BaseFilter):
    """工作经历筛选器"""
    
    async def filter(self, job_data: Dict, resume_data: Dict) -> FilterResult:
        """筛选：工作经历要求（使用LLM匹配）"""
        qualification = job_data.get("资格条件", [])
        work_exp_requirement = RequirementExtractor.extract_work_experience_requirement(qualification)
        
        if not work_exp_requirement:
            return FilterResult(
                passed=True,
                reason="岗位未明确工作经历要求",
                source="rule"
            )
        
        # 使用LLM匹配
        return await self.llm_matcher.match_work_experience_llm(work_exp_requirement, resume_data)
