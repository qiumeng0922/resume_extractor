#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
政治面貌筛选器
"""

from typing import Dict
from core.models import FilterResult
from filters.base import BaseFilter
from extractors.requirement_extractor import RequirementExtractor
from matchers.rule_matcher import RuleMatcher


class PoliticalStatusFilter(BaseFilter):
    """政治面貌筛选器"""
    
    async def filter(self, job_data: Dict, resume_data: Dict) -> FilterResult:
        """筛选：政治面貌要求"""
        # 岗位可能没有明确的政治面貌要求，需要从岗位职责或资格条件中提取
        qualification = job_data.get("资格条件", [])
        job_duty = job_data.get("岗位职责", [])
        
        political_requirement = RequirementExtractor.extract_political_requirement(qualification, job_duty)
        
        if not political_requirement:
            return FilterResult(
                passed=True,
                reason="岗位未明确政治面貌要求",
                source="rule"
            )
        
        # 提取简历政治面貌
        basic_info = resume_data.get("基本信息", {})
        political_status = basic_info.get("政治面貌", "")
        
        # 规则匹配
        result = self.rule_matcher.match_political_rule(political_requirement, political_status)
        
        if result["matched"]:
            return FilterResult(
                passed=True,
                reason=result["reason"],
                source="rule",
                details=result
            )
        else:
            return FilterResult(
                passed=False,
                reason=result["reason"],
                source="rule",
                details=result
            )
