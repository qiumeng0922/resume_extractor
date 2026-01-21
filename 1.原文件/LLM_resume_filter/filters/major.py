#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业筛选器
"""

from typing import Dict
from core.models import FilterResult
from filters.base import BaseFilter
from extractors.requirement_extractor import RequirementExtractor
from extractors.resume_extractor import ResumeExtractor
from matchers.rule_matcher import RuleMatcher
from matchers.llm_matcher import LLMMatcher
from utils.logger_config import setup_logger

logger = setup_logger("major_filter")


class MajorFilter(BaseFilter):
    """专业筛选器"""
    
    def __init__(self, model_manager=None, rule_matcher=None, llm_matcher=None, major_library=None):
        """
        初始化专业筛选器
        
        Args:
            model_manager: 模型管理器
            rule_matcher: 规则匹配器
            llm_matcher: LLM匹配器
            major_library: 专业库管理器
        """
        super().__init__(model_manager, rule_matcher, llm_matcher)
        self.major_library = major_library
    
    async def filter(self, job_data: Dict, resume_data: Dict) -> FilterResult:
        """筛选：专业要求"""
        qualification = job_data.get("资格条件", [])
        major_requirement = RequirementExtractor.extract_major_requirement(qualification)
        
        if not major_requirement:
            return FilterResult(
                passed=True,
                reason="岗位未明确专业要求",
                source="rule"
            )
        
        # 提取简历中的所有专业名称
        major_names = ResumeExtractor.extract_majors_from_resume(resume_data)
        if not major_names:
            logger.debug("专业筛选：简历中无专业信息")
            return FilterResult(
                passed=False,
                reason="简历中无专业信息",
                source="rule",
                details={"method": "规则匹配-数据缺失"}
            )
        
        # 查找专业对应的专业类
        major_classes = self.major_library.get_major_classes(major_names) if self.major_library else []
        logger.debug(f"专业筛选：简历专业={major_names}，对应专业类={major_classes}")
        
        work_experience = resume_data.get("主要工作经历", [])
        
        # 规则匹配（先进行专业类匹配）
        result = self.rule_matcher.match_major_rule(major_requirement, major_names, major_classes, work_experience)
        
        # 如果规则匹配成功，直接返回
        if result["matched"]:
            return FilterResult(
                passed=True,
                reason=result["reason"],
                source="rule",
                details=result
            )
        
        # 如果规则匹配失败，且需要LLM判断
        if result.get("need_llm", False):
            logger.debug("专业筛选：专业类不匹配，使用LLM判断")
            return await self.llm_matcher.match_major_llm(major_requirement, major_names, resume_data)
        
        # 规则匹配失败，且不需要LLM判断（可能是经历匹配失败）
        return FilterResult(
            passed=False,
            reason=result["reason"],
            source="rule",
            details=result
        )
