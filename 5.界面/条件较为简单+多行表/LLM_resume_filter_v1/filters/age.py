#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
年龄筛选器
"""

import re
from typing import Dict, Optional
from core.models import FilterResult
from filters.base import BaseFilter
from extractors.requirement_extractor import RequirementExtractor
from matchers.rule_matcher import RuleMatcher
from utils.calculator import Calculator
from utils.logger_config import setup_logger

logger = setup_logger("age_filter")


class AgeFilter(BaseFilter):
    """年龄筛选器"""
    
    def __init__(self, model_manager=None, rule_matcher=None, llm_matcher=None):
        super().__init__(model_manager, rule_matcher, llm_matcher)
        self.calculator = Calculator()
    
    def _normalize_age_requirement(self, age_requirement) -> Optional[Dict]:
        """
        规范化年龄要求，转换为包含 max_age 的字典格式
        
        Args:
            age_requirement: 年龄要求，可能是字符串、字典或None
            
        Returns:
            包含 max_age 的字典，如果无法解析则返回None
        """
        if not age_requirement:
            return None
        
        # 如果已经是包含 max_age 的字典，直接返回
        if isinstance(age_requirement, dict) and "max_age" in age_requirement:
            return age_requirement
        
        # 如果是字符串，尝试解析
        if isinstance(age_requirement, str):
            # 处理 "≤40" 格式
            if "≤" in age_requirement:
                try:
                    max_age = int(age_requirement.replace("≤", "").strip())
                    return {"max_age": max_age}
                except ValueError:
                    pass
            
            # 处理 "一般不超过XX周岁" 格式
            pattern = r"一般不超过(\d+)周岁"
            match = re.search(pattern, age_requirement)
            if match:
                try:
                    max_age = int(match.group(1))
                    return {"max_age": max_age}
                except ValueError:
                    pass
        
        # 如果是字典但包含 "原文" 键，从原文中提取
        if isinstance(age_requirement, dict) and "原文" in age_requirement:
            original_text = age_requirement["原文"]
            if isinstance(original_text, str):
                # 处理 "≤40" 格式
                if "≤" in original_text:
                    try:
                        max_age = int(original_text.replace("≤", "").strip())
                        return {"max_age": max_age}
                    except ValueError:
                        pass
                
                # 处理 "一般不超过XX周岁" 格式
                pattern = r"一般不超过(\d+)周岁"
                match = re.search(pattern, original_text)
                if match:
                    try:
                        max_age = int(match.group(1))
                        return {"max_age": max_age}
                    except ValueError:
                        pass
        
        return None
    
    async def filter(self, job_data: Dict, resume_data: Dict) -> FilterResult:
        """筛选：年龄要求"""
        qualification = job_data.get("资格条件", [])
        age_requirement_raw = RequirementExtractor.extract_age_requirement(qualification)
        
        # 规范化年龄要求
        age_requirement = self._normalize_age_requirement(age_requirement_raw)
        
        if not age_requirement:
            logger.debug("年龄筛选：岗位未明确年龄要求，默认通过")
            return FilterResult(
                passed=True,
                reason="岗位未明确年龄要求",
                source="rule",
                details={"method": "规则匹配-无要求"}
            )
        
        # 提取简历年龄信息
        basic_info = resume_data.get("基本信息", {})
        birth_date = basic_info.get("出生日期", "")
        
        if not birth_date:
            logger.warning(f"年龄筛选：简历中缺少出生日期信息")
            return FilterResult(
                passed=False,
                reason="简历中缺少出生日期信息",
                source="rule",
                details={"method": "规则匹配-数据缺失"}
            )
        
        # 计算年龄
        age = self.calculator.calculate_age(birth_date)
        max_age = age_requirement.get("max_age")
        logger.debug(f"年龄筛选：出生日期={birth_date}，计算年龄={age}岁，要求≤{max_age}岁")
        
        # 规则匹配
        result = self.rule_matcher.match_age_rule(age_requirement, age)
        
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
