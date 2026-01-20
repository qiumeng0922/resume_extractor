#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学历筛选器
"""

from typing import Dict
from core.models import FilterResult
from filters.base import BaseFilter
from extractors.requirement_extractor import RequirementExtractor


class EducationFilter(BaseFilter):
    """学历筛选器"""
    
    async def filter(self, job_data: Dict, resume_data: Dict) -> FilterResult:
        """筛选：学历要求"""
        qualification = job_data.get("资格条件", [])
        education_requirement = RequirementExtractor.extract_education_requirement(qualification)
        
        if not education_requirement:
            return FilterResult(
                passed=True,
                reason="岗位未明确学历要求",
                source="rule"
            )
        
        # 提取简历学历信息（只使用最高学历相关字段）
        education_info = resume_data.get("学习经历统计信息", {})
        highest_education = education_info.get("最高学历", "")
        highest_school = education_info.get("最高学历毕业院校", "")
        highest_school_type = education_info.get("最高学历毕业院校类型", "")
        
        # 规则匹配（只传递最高学历相关字段）
        result = self.rule_matcher.match_education_rule(
            education_requirement, highest_education, "", 
            highest_school, highest_school_type, ""
        )
        
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
