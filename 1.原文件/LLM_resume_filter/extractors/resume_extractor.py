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
        从简历中提取所有专业名称（去除括号和学位信息）
        
        Args:
            resume_data: 简历数据
        
        Returns:
            专业名称列表（去重）
        """
        education_info = resume_data.get("学习经历统计信息", {})
        major_field = education_info.get("专业", "")
        
        if not major_field:
            return []
        
        # 解析专业字段，格式： "专业1(学位1)\n专业2(学位2)"
        majors = []
        # 按换行符分割
        lines = major_field.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # 使用正则表达式提取专业名称（去除括号和括号内的内容）
            # 匹配格式：专业名称(学位) 或 专业名称
            match = re.match(r'^([^(]+?)(?:\([^)]+\))?$', line)
            if match:
                major_name = match.group(1).strip()
                if major_name:
                    majors.append(major_name)
        
        # 去重并返回
        return list(set(majors))
