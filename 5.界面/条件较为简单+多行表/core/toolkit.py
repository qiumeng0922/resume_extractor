#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
筛选工具箱模块
"""

from typing import Dict, Optional
from core.models import FilterResult
from filters.education import EducationFilter
from filters.major import MajorFilter
from filters.age import AgeFilter
from filters.performance import PerformanceFilter
from filters.title import TitleFilter
from filters.work_experience import WorkExperienceFilter
from filters.work_years import WorkYearsFilter
from filters.political_status import PoliticalStatusFilter
from matchers.rule_matcher import RuleMatcher
from matchers.llm_matcher import LLMMatcher
from utils.major_library import MajorLibrary


class ResumeFilterToolkit:
    """简历筛选工具箱"""
    
    def __init__(self, model_manager=None, major_library_path: Optional[str] = None, school_library_path: Optional[str] = None):
        """
        初始化工具箱
        
        Args:
            model_manager: 模型管理器（用于LLM筛选）
            major_library_path: 专业库.json文件路径
            school_library_path: 院校库.json文件路径
        """
        self.model_manager = model_manager
        
        # 初始化专业库
        self.major_library = MajorLibrary(major_library_path)
        
        # 初始化匹配器
        self.rule_matcher = RuleMatcher(school_library_path=school_library_path)
        self.llm_matcher = LLMMatcher(model_manager)
        
        # 初始化筛选器
        self.education_filter = EducationFilter(model_manager, self.rule_matcher, self.llm_matcher)
        self.major_filter = MajorFilter(model_manager, self.rule_matcher, self.llm_matcher, self.major_library)
        self.age_filter = AgeFilter(model_manager, self.rule_matcher, self.llm_matcher)
        self.performance_filter = PerformanceFilter(model_manager, self.rule_matcher, self.llm_matcher)
        self.title_filter = TitleFilter(model_manager, self.rule_matcher, self.llm_matcher)
        self.work_experience_filter = WorkExperienceFilter(model_manager, self.rule_matcher, self.llm_matcher)
        self.work_years_filter = WorkYearsFilter(model_manager, self.rule_matcher, self.llm_matcher)
        self.political_status_filter = PoliticalStatusFilter(model_manager, self.rule_matcher, self.llm_matcher)
    
    async def filter_education(self, job_data: Dict, resume_data: Dict) -> FilterResult:
        """筛选：学历要求"""
        return await self.education_filter.filter(job_data, resume_data)
    
    async def filter_major(self, job_data: Dict, resume_data: Dict) -> FilterResult:
        """筛选：专业要求"""
        return await self.major_filter.filter(job_data, resume_data)
    
    async def filter_age(self, job_data: Dict, resume_data: Dict) -> FilterResult:
        """筛选：年龄要求"""
        return await self.age_filter.filter(job_data, resume_data)
    
    async def filter_performance(self, job_data: Dict, resume_data: Dict) -> FilterResult:
        """筛选：绩效要求"""
        return await self.performance_filter.filter(job_data, resume_data)
    
    async def filter_work_experience(self, job_data: Dict, resume_data: Dict) -> FilterResult:
        """筛选：工作经历要求"""
        return await self.work_experience_filter.filter(job_data, resume_data)
    
    async def filter_work_years(self, job_data: Dict, resume_data: Dict) -> FilterResult:
        """筛选：工作经验要求"""
        return await self.work_years_filter.filter(job_data, resume_data)
    
    async def filter_political_status(self, job_data: Dict, resume_data: Dict) -> FilterResult:
        """筛选：政治面貌要求"""
        return await self.political_status_filter.filter(job_data, resume_data)
    
    async def filter_professional_title(self, job_data: Dict, resume_data: Dict) -> FilterResult:
        """筛选：职称要求"""
        return await self.title_filter.filter(job_data, resume_data)
