#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
岗位要求提取器模块
"""

from typing import Dict, List, Optional
from utils.logger_config import setup_logger

logger = setup_logger("requirement_extractor")


class RequirementExtractor:
    """岗位要求提取器"""
    
    @staticmethod
    def get_normalized_value(requirement_list: List) -> Optional[Dict]:
        """
        从要求列表中提取规整后的值，如果规整后为空则使用原文
        
        Args:
            requirement_list: 要求列表，格式如 [{"原文":"...", "规整后":...}]
        
        Returns:
            规整后的值（如果存在且不为空），否则返回原文，如果都不存在则返回None
        """
        if not isinstance(requirement_list, list) or not requirement_list:
            return None
        
        original_text = None
        normalized_value = None
        
        for item in requirement_list:
            if isinstance(item, dict):
                if "原文" in item:
                    original_text = item["原文"]
                if "规整后" in item:
                    normalized = item["规整后"]
                    # 检查规整后的值是否为空
                    if normalized is not None and normalized != "" and normalized != []:
                        normalized_value = normalized
        
        # 优先返回规整后的值，如果为空则返回原文
        if normalized_value is not None:
            return normalized_value
        elif original_text is not None and original_text != "":
            return {"原文": original_text}
        else:
            return None
    
    @staticmethod
    def extract_education_requirement(qualification: List) -> Optional[Dict]:
        """
        提取学历要求（仅支持新格式）
        
        Args:
            qualification: 资格条件列表
        
        Returns:
            规整后的值（如果存在且不为空），否则返回原文
        """
        if not isinstance(qualification, list):
            return None
        
        for item in qualification:
            if isinstance(item, dict) and "学历要求" in item:
                edu_req = item["学历要求"]
                return RequirementExtractor.get_normalized_value(edu_req)
        return None
    
    @staticmethod
    def extract_major_requirement(qualification: List) -> Optional[Dict]:
        """
        提取专业要求（仅支持新格式）
        
        Args:
            qualification: 资格条件列表
        
        Returns:
            规整后的值（如果存在且不为空），否则返回原文
        """
        if not isinstance(qualification, list):
            return None
        
        for item in qualification:
            if isinstance(item, dict) and "专业要求" in item:
                major_req = item["专业要求"]
                return RequirementExtractor.get_normalized_value(major_req)
        return None
    
    @staticmethod
    def extract_age_requirement(qualification: List) -> Optional[Dict]:
        """
        提取年龄要求（仅支持新格式）
        
        Args:
            qualification: 资格条件列表
        
        Returns:
            规整后的值（如果存在且不为空），否则返回原文
        """
        if not isinstance(qualification, list):
            return None
        
        for item in qualification:
            if isinstance(item, dict) and "年龄要求" in item:
                age_req = item["年龄要求"]
                return RequirementExtractor.get_normalized_value(age_req)
        return None
    
    @staticmethod
    def extract_performance_requirement(qualification: List) -> Optional[Dict]:
        """
        提取绩效要求（仅支持新格式）
        
        Args:
            qualification: 资格条件列表
        
        Returns:
            规整后的值（如果存在且不为空），否则返回原文
        """
        if not isinstance(qualification, list):
            return None
        
        for item in qualification:
            if isinstance(item, dict) and "绩效要求" in item:
                perf_req = item["绩效要求"]
                return RequirementExtractor.get_normalized_value(perf_req)
        return None
    
    @staticmethod
    def extract_work_experience_requirement(qualification: List) -> Optional[Dict]:
        """
        提取工作经历要求（仅支持新格式）
        
        Args:
            qualification: 资格条件列表
        
        Returns:
            规整后的值（如果存在且不为空），否则返回原文
        """
        if not isinstance(qualification, list):
            return None
        
        for item in qualification:
            if isinstance(item, dict) and "工作经历" in item:
                work_exp_req = item["工作经历"]
                return RequirementExtractor.get_normalized_value(work_exp_req)
        return None
    
    @staticmethod
    def extract_work_years_requirement(job_requirement: List) -> Optional[Dict]:
        """
        提取工作经验年数要求（仅支持新格式）
        
        Args:
            job_requirement: 岗位任职条件列表
        
        Returns:
            规整后的值（如果存在且不为空），否则返回原文
        """
        if not isinstance(job_requirement, list):
            return None
        
        for item in job_requirement:
            if isinstance(item, dict) and "工作经验" in item:
                work_years_req = item["工作经验"]
                return RequirementExtractor.get_normalized_value(work_years_req)
        return None
    
    @staticmethod
    def extract_political_requirement(qualification: List, job_duty: List) -> Optional[str]:
        """
        提取政治面貌要求
        
        Args:
            qualification: 资格条件列表
            job_duty: 岗位职责列表
        
        Returns:
            政治面貌要求字符串，如果没有则返回None
        """
        # 从资格条件中查找
        if isinstance(qualification, list):
            for item in qualification:
                if isinstance(item, dict) and "政治面貌" in item:
                    political_req = item["政治面貌"]
                    normalized = RequirementExtractor.get_normalized_value(political_req)
                    if normalized:
                        if isinstance(normalized, dict) and "原文" in normalized:
                            return normalized["原文"]
                        elif isinstance(normalized, str):
                            return normalized
        
        # 从岗位职责中查找（某些岗位可能在职责中说明）
        if isinstance(job_duty, list):
            for duty in job_duty:
                if isinstance(duty, str) and ("党员" in duty or "政治面貌" in duty):
                    return duty
        
        return None
    
    @staticmethod
    def extract_title_requirement(qualification: List) -> Optional[Dict]:
        """
        提取职称要求（仅支持新格式）
        
        Args:
            qualification: 资格条件列表
        
        Returns:
            规整后的值（如果存在且不为空），否则返回原文
        """
        if not isinstance(qualification, list):
            return None
        
        for item in qualification:
            if isinstance(item, dict) and "职称要求" in item:
                title_req = item["职称要求"]
                return RequirementExtractor.get_normalized_value(title_req)
        return None
