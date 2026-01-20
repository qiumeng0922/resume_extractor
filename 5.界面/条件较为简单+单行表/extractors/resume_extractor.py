#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历数据提取器模块
"""

import re
from typing import Dict, List
from utils.logger_config import setup_logger

logger = setup_logger("resume_extractor")


class ResumeExtractor:
    """简历数据提取器"""
    
    @staticmethod
    def extract_majors_from_resume(resume_data: Dict) -> List[str]:
        """
        从简历中提取专业名称（只使用最高学历所学专业）
        
        Args:
            resume_data: 简历数据
        
        Returns:
            专业名称列表
        """
        education_info = resume_data.get("学习经历统计信息", {})
        # 只使用最高学历所学专业
        major_field = education_info.get("最高学历所学专业", "")
        
        if not major_field:
            return []
        
        # 返回最高学历所学专业（单个专业）
        major_name = major_field.strip()
        if major_name:
            return [major_name]
        
        return []
