#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作经验筛选器
"""

from typing import Dict
from core.models import FilterResult
from filters.base import BaseFilter
from matchers.llm_matcher import LLMMatcher
from extractors.requirement_extractor import RequirementExtractor
from utils.logger_config import setup_logger

logger = setup_logger("work_years_filter")


class WorkYearsFilter(BaseFilter):
    """工作经验筛选器"""
    
    async def filter(self, job_data: Dict, resume_data: Dict) -> FilterResult:
        """
        筛选：工作经验要求
        逻辑：先获取"工作经验"的"原文"字段判断是否有"相关工作经验"或"相关经验"关键词
        - 如有：进行相关工作经验判断（LLM）+ 工作年限判断（规则）
        - 如无：只进行工作年限判断（规则）
        """
        # 检查是否有岗位职责或岗位任职条件
        job_duty = job_data.get("岗位职责", [])
        job_requirement = job_data.get("岗位任职条件", [])
        
        if not job_duty and not job_requirement:
            return FilterResult(
                passed=True,
                reason="岗位未明确工作经验要求（无岗位职责和岗位任职条件）",
                source="rule"
            )
        
        # 提取工作经验要求（包含原文和规整后的值）
        work_years_requirement = RequirementExtractor.extract_work_years_requirement(job_requirement)
        
        # 判断是否需要进行相关工作经验判断
        need_llm_match = False
        original_text = ""
        
        if work_years_requirement:
            # 提取原文
            if isinstance(work_years_requirement, dict):
                original_text = work_years_requirement.get("原文", "")
            
            # 判断原文中是否包含"相关工作经验"、"相关经验"、"相关岗位工作经验"等关键词
            keywords = ["相关工作经验", "相关经验", "相关岗位工作经验", "相关研究经验"]
            if original_text and any(keyword in original_text for keyword in keywords):
                need_llm_match = True
                logger.debug(f"工作经验筛选：检测到需要相关工作经验判断，原文={original_text}")
            else:
                logger.debug(f"工作经验筛选：无需相关工作经验判断，原文={original_text}")
        
        # 如果需要相关工作经验判断，使用LLM匹配
        if need_llm_match:
            logger.debug("工作经验筛选：使用LLM进行相关工作经验判断")
            llm_result = await self.llm_matcher.match_work_years_llm(work_years_requirement, job_data, resume_data)
            
            # 如果LLM判断不通过，直接返回
            if not llm_result.passed:
                return llm_result
            
            # LLM判断通过后，继续进行工作年限判断
            logger.debug("工作经验筛选：LLM判断通过，继续进行工作年限判断")
        
        # 进行工作年限判断（规则匹配）
        if work_years_requirement:
            logger.debug("工作经验筛选：使用规则进行工作年限判断")
            basic_info = resume_data.get("基本信息", {})
            join_date = basic_info.get("参加工作时间", "")
            work_experience = resume_data.get("主要工作经历", [])
            
            result = self.rule_matcher.match_work_years_rule(work_years_requirement, work_experience, join_date)
            
            return FilterResult(
                passed=result["matched"],
                reason=result["reason"],
                source="rule",
                details=result
            )
        
        # 如果没有提取到工作经验要求，但有岗位职责或岗位任职条件，默认通过
        return FilterResult(
            passed=True,
            reason="岗位未明确工作年限要求",
            source="rule"
        )
