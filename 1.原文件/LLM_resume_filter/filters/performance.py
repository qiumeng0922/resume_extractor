#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
绩效筛选器
"""

from typing import Dict
from core.models import FilterResult
from filters.base import BaseFilter
from extractors.requirement_extractor import RequirementExtractor
from matchers.rule_matcher import RuleMatcher
from matchers.llm_matcher import LLMMatcher


class PerformanceFilter(BaseFilter):
    """绩效筛选器"""
    
    async def filter(self, job_data: Dict, resume_data: Dict) -> FilterResult:
        """筛选：绩效要求（异步方法，支持并发LLM调用）"""
        qualification = job_data.get("资格条件", [])
        performance_requirement = RequirementExtractor.extract_performance_requirement(qualification)
        
        if not performance_requirement:
            return FilterResult(
                passed=True,
                reason="岗位未明确绩效要求",
                source="rule"
            )
        
        # 简历中可能没有绩效信息，需要LLM判断或默认通过
        # 这里先用规则，如果无法判断则使用LLM
        performance_data = resume_data.get("年度绩效情况", {})
        has_performance_info = performance_data and isinstance(performance_data, dict) and len(performance_data) > 0
        
        if has_performance_info:
            # 有绩效信息，先尝试规则匹配
            result = self.rule_matcher.match_performance_rule(performance_requirement, resume_data)
            if result.get("matched") and result.get("reason") != "简历中有绩效信息，但需要LLM判断":
                return FilterResult(
                    passed=result["matched"],
                    reason=result["reason"],
                    source="rule",
                    details=result
                )
        
        # 使用LLM判断（异步）
        return await self.llm_matcher.match_performance_llm(performance_requirement, resume_data)
