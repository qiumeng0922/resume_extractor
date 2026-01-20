#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
职称筛选器
"""

from typing import Dict
from core.models import FilterResult
from filters.base import BaseFilter
from extractors.requirement_extractor import RequirementExtractor
from matchers.rule_matcher import RuleMatcher
from matchers.llm_matcher import LLMMatcher


class TitleFilter(BaseFilter):
    """职称筛选器"""
    
    async def filter(self, job_data: Dict, resume_data: Dict) -> FilterResult:
        """筛选：职称要求（异步方法，支持并发LLM调用）"""
        qualification = job_data.get("资格条件", [])
        title_requirement = RequirementExtractor.extract_title_requirement(qualification)
        
        if not title_requirement:
            return FilterResult(
                passed=True,
                reason="岗位未明确职称要求",
                source="rule"
            )
        
        # 简历中可能没有职称信息，需要LLM判断
        # 检查简历中是否有职称信息
        has_title_info = False
        if "职称证书" in resume_data:
            title_certs = resume_data["职称证书"]
            if title_certs and isinstance(title_certs, list) and len(title_certs) > 0:
                has_title_info = True
        
        if not has_title_info and "证书统计信息" in resume_data:
            cert_stats = resume_data["证书统计信息"]
            if cert_stats and isinstance(cert_stats, dict):
                if cert_stats.get("职称等级（最高）") or cert_stats.get("职称名称"):
                    has_title_info = True
        
        if has_title_info:
            # 有职称信息，先尝试规则匹配
            result = self.rule_matcher.match_title_rule(title_requirement, resume_data)
            if result.get("matched") and result.get("reason") != "简历中有职称信息，但需要LLM判断":
                return FilterResult(
                    passed=result["matched"],
                    reason=result["reason"],
                    source="rule",
                    details=result
                )
        
        # 使用LLM判断（异步）
        return await self.llm_matcher.match_title_llm(title_requirement, resume_data)
