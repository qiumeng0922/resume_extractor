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
        
        # 提取最高学历的学习形式（全日制/非全日制）
        # 方法1：从"主要学习经历"中找到最高学历对应的学习形式
        learning_experiences = resume_data.get("主要学习经历", [])
        highest_education_form = ""  # 学习形式：全日制教育/非全日制教育
        highest_education_degree = education_info.get("最高学历学位", "")  # 可能包含"非全日制"字样
        
        # 从主要学习经历中找到最高学历对应的学习形式
        for exp in learning_experiences:
            if isinstance(exp, dict):
                exp_education = exp.get("学历", "")
                exp_form = exp.get("学习形式", "")
                # 如果学历匹配最高学历，记录学习形式
                if exp_education == highest_education:
                    highest_education_form = exp_form
                    break
        
        # 方法2：如果主要学习经历中没有找到，从"最高学历学位"字段判断
        if not highest_education_form and highest_education_degree:
            if "非全日制" in highest_education_degree:
                highest_education_form = "非全日制教育"
            elif "全日制" in highest_education_degree:
                highest_education_form = "全日制教育"
        
        # 规则匹配（传递最高学历相关字段和学习形式）
        result = self.rule_matcher.match_education_rule(
            education_requirement, highest_education, "", 
            highest_school, highest_school_type, "",
            highest_education_form  # 传递学习形式
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
