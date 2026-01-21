#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则匹配器模块
"""

import re
import os
import json
from typing import Dict, List, Optional
from utils.logger_config import setup_logger
from utils.calculator import Calculator

logger = setup_logger("rule_matcher")


class RuleMatcher:
    """规则匹配器 - 所有规则匹配逻辑"""
    
    def __init__(self, school_library_path: str = None):
        """
        初始化规则匹配器
        
        Args:
            school_library_path: 院校库JSON文件路径，如果为None则自动查找
        """
        self.calculator = Calculator()
        self.school_library = self._load_school_library(school_library_path)
    
    def _load_school_library(self, school_library_path: Optional[str] = None) -> Dict:
        """
        加载院校库
        
        Args:
            school_library_path: 院校库JSON文件路径
            
        Returns:
            院校库字典，key为院校名称，value为属性标签列表
        """
        if school_library_path is None:
            # 自动查找院校库文件
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 从 matchers 目录向上到项目根目录，然后到 data 目录
            project_root = os.path.dirname(os.path.dirname(current_dir))
            school_library_path = os.path.join(project_root, "data", "院校库.json")
        
        school_library = {}
        try:
            if os.path.exists(school_library_path):
                with open(school_library_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 解析院校库数据
                    if "院校库列表" in data:
                        for school in data["院校库列表"]:
                            school_name = school.get("院校中文名称", "")
                            attributes = school.get("属性标签", [])
                            if school_name:
                                school_library[school_name] = attributes
                    logger.info(f"✅ 已加载院校库，共 {len(school_library)} 所院校")
            else:
                logger.warning(f"⚠️ 院校库文件不存在: {school_library_path}")
        except Exception as e:
            logger.error(f"❌ 加载院校库失败: {e}")
        
        return school_library
    
    def _check_school_attributes(self, school_name: str, required_attributes: List[str]) -> bool:
        """
        检查学校是否具有指定的属性标签
        
        Args:
            school_name: 学校名称
            required_attributes: 需要的属性标签列表（如["985", "211"]）
            
        Returns:
            如果学校具有所有需要的属性标签，返回True
        """
        if not school_name or not self.school_library:
            return False
        
        # 在院校库中查找学校
        school_attributes = self.school_library.get(school_name, [])
        if not school_attributes:
            # 尝试模糊匹配（去除空格、括号等）
            school_name_clean = school_name.replace(" ", "").replace("（", "(").replace("）", ")")
            for lib_school_name, lib_attributes in self.school_library.items():
                lib_school_name_clean = lib_school_name.replace(" ", "").replace("（", "(").replace("）", ")")
                if school_name_clean == lib_school_name_clean or school_name_clean in lib_school_name_clean or lib_school_name_clean in school_name_clean:
                    school_attributes = lib_attributes
                    break
        
        # 检查是否包含所有需要的属性
        if not school_attributes:
            return False
        
        # 检查是否包含任一需要的属性（通常985/211是"或"关系）
        for req_attr in required_attributes:
            if req_attr in school_attributes:
                return True
        
        return False
    
    def match_education_rule(self, requirement: Dict, highest_edu: str, fulltime_edu: str, 
                            highest_school: str, highest_school_type: str, fulltime_school_type: str,
                            highest_education_form: str = "") -> Dict:
        """
        匹配学历规则
        
        Args:
            requirement: 岗位学历要求
            highest_edu: 简历最高学历
            fulltime_edu: 简历全日制学历（保留参数，未使用）
            highest_school: 简历最高学历毕业院校
            highest_school_type: 简历最高学历毕业院校类型
            fulltime_school_type: 简历全日制毕业院校类型（保留参数，未使用）
            highest_education_form: 简历最高学历的学习形式（"全日制教育"或"非全日制教育"）
        """
        edu_levels = {
            "博士": 5,
            "硕士研究生": 4,
            "硕士": 4,
            "大学本科": 3,
            "本科": 3,
            "专科": 2,
            "高中": 1
        }
        
        # 处理规整后的结构化数据
        if isinstance(requirement, dict):
            # 检查是否有规整后的结构化数据
            if "条件" in requirement and "排名" in requirement:
                # 规整后格式：{"条件":"或","排名":[...],"学历":[...]}
                condition = requirement.get("条件", "或")
                rankings = requirement.get("排名", [])
                educations = requirement.get("学历", [])
                
                # 检查排名要求（985/211等）
                matched_ranking = False
                if rankings:
                    for rank_req in rankings:
                        if isinstance(rank_req, str) and ("985" in rank_req or "211" in rank_req):
                            # 优先使用院校库判断，如果没有则使用学校类型字段
                            required_attrs = []
                            if "985" in rank_req:
                                required_attrs.append("985")
                            if "211" in rank_req:
                                required_attrs.append("211")
                            
                            # 使用院校库判断
                            if highest_school and self.school_library:
                                matched_ranking = self._check_school_attributes(highest_school, required_attrs)
                            else:
                                # 降级使用学校类型字段
                                matched_ranking = "985" in highest_school_type or "211" in highest_school_type
                            
                            if matched_ranking:
                                break
                
                # 检查学历要求
                matched_education = False
                req_level = 0
                has_985_211_in_education = False  # 初始化变量
                required_attributes = []  # 需要的学校属性
                requires_fulltime = False  # 是否要求全日制
                
                for edu_req in educations:
                    if isinstance(edu_req, str):
                        # 检查学历要求中是否包含"全日制"关键词
                        if "全日制" in edu_req:
                            requires_fulltime = True
                        # 检查学历要求中是否包含985/211
                        if "985" in edu_req or "211" in edu_req:
                            has_985_211_in_education = True
                            if "985" in edu_req:
                                required_attributes.append("985")
                            if "211" in edu_req:
                                required_attributes.append("211")
                        # 提取学历等级
                        for edu, level in edu_levels.items():
                            if edu in edu_req:
                                req_level = max(req_level, level)
                
                # 检查排名要求中是否包含"全日制"关键词
                for rank_req in rankings:
                    if isinstance(rank_req, str) and "全日制" in rank_req:
                        requires_fulltime = True
                
                # 提取简历中的学历等级（只使用最高学历）
                resume_level = 0
                for edu, level in edu_levels.items():
                    if edu in highest_edu:
                        resume_level = max(resume_level, level)
                
                # 检查简历学校是否满足985/211要求（只使用最高学历毕业院校类型）
                has_985_211_resume = False
                if has_985_211_in_education and required_attributes:
                    # 优先使用院校库判断
                    if highest_school and self.school_library:
                        has_985_211_resume = self._check_school_attributes(highest_school, required_attributes)
                    else:
                        # 降级使用学校类型字段（只使用最高学历毕业院校类型）
                        has_985_211_resume = "985" in highest_school_type or "211" in highest_school_type
                else:
                    # 如果没有985/211要求，检查学校类型字段作为备用（只使用最高学历毕业院校类型）
                    has_985_211_resume = "985" in highest_school_type or "211" in highest_school_type
                
                # 检查全日制/非全日制要求
                matched_fulltime = True  # 默认匹配（如果没有全日制要求）
                if requires_fulltime:
                    # 如果岗位要求全日制，简历必须是全日制
                    if highest_education_form == "全日制教育":
                        matched_fulltime = True
                    elif highest_education_form == "非全日制教育" or "非全日制" in highest_education_form:
                        matched_fulltime = False
                    else:
                        # 如果学习形式字段为空，尝试从其他字段判断
                        # 如果无法确定，默认不匹配（严格模式）
                        matched_fulltime = False
                
                # 判断学历要求是否匹配
                if has_985_211_in_education:
                    # 如果学历要求中包含985/211，必须同时满足学历等级、学校属性和全日制要求
                    matched_education = (resume_level >= req_level) and has_985_211_resume and matched_fulltime
                else:
                    # 如果学历要求中不包含985/211，需要满足学历等级和全日制要求
                    matched_education = (resume_level >= req_level) and matched_fulltime
                
                # 判断：如果是"或"条件，满足任一即可
                if condition == "或":
                    matched = matched_ranking or matched_education
                else:
                    matched = matched_ranking and matched_education
                
                # 构建详细信息（只使用最高学历相关字段）
                resume_info = f"简历信息：最高学历={highest_edu}，最高学历毕业院校={highest_school}，学校类型={highest_school_type}，学习形式={highest_education_form if highest_education_form else '未明确'}"
                requirement_info = f"岗位要求：条件={condition}，排名要求={rankings}，学历要求={educations}"
                
                # 将学历等级转换为可读名称
                def get_edu_name(level):
                    """将学历等级数字转换为可读名称"""
                    level_names = {5: "博士", 4: "硕士研究生", 3: "大学本科", 2: "专科", 1: "高中"}
                    return level_names.get(level, f"{level}级")
                
                resume_edu_name = get_edu_name(resume_level)
                req_edu_name = get_edu_name(req_level)
                
                # 构建匹配详情
                match_parts = []
                if rankings:
                    match_parts.append(f"排名匹配={matched_ranking}")
                if educations:
                    if has_985_211_in_education:
                        school_check_method = "院校库" if (highest_school and self.school_library) else "学校类型字段"
                        edu_level_desc = f"学历等级：{resume_edu_name}（{resume_level}级）≥{req_edu_name}（{req_level}级）"
                        school_attr_desc = f"学校属性：{'满足' if has_985_211_resume else '不满足'}985/211要求（判断方法：{school_check_method}）"
                        fulltime_desc = f"学习形式：{'满足' if matched_fulltime else '不满足'}全日制要求（简历：{highest_education_form if highest_education_form else '未明确'}，岗位要求：全日制）" if requires_fulltime else ""
                        if fulltime_desc:
                            match_parts.append(f"学历匹配={matched_education}（{edu_level_desc}，{school_attr_desc}，{fulltime_desc}）")
                        else:
                            match_parts.append(f"学历匹配={matched_education}（{edu_level_desc}，{school_attr_desc}）")
                    else:
                        edu_level_desc = f"学历等级：{resume_edu_name}（{resume_level}级）≥{req_edu_name}（{req_level}级）"
                        fulltime_desc = f"学习形式：{'满足' if matched_fulltime else '不满足'}全日制要求（简历：{highest_education_form if highest_education_form else '未明确'}，岗位要求：全日制）" if requires_fulltime else ""
                        if fulltime_desc:
                            match_parts.append(f"学历匹配={matched_education}（{edu_level_desc}，{fulltime_desc}）")
                        else:
                            match_parts.append(f"学历匹配={matched_education}（{edu_level_desc}）")
                
                match_detail = f"满足{'任一' if condition == '或' else '所有'}条件：{', '.join(match_parts)}"
                detail = f"{resume_info}；{requirement_info}；{match_detail}"
                
                method = f"规则匹配-结构化数据（条件：{condition}）"
                logger.debug(f"学历筛选：使用{method}，排名要求={rankings}，学历要求={educations}")
                logger.debug(f"学历筛选结果：{match_detail}")
                
                if matched:
                    reason_suffix = ""
                    if requires_fulltime and not matched_fulltime:
                        reason_suffix = f"（不满足全日制要求：简历为{highest_education_form if highest_education_form else '非全日制'}）"
                    return {
                        "matched": True,
                        "reason": f"学历符合要求：简历{highest_edu}（{highest_school_type}）{reason_suffix}，岗位要求{requirement}",
                        "method": method,
                        "detail": detail,
                        "resume_education": highest_edu,
                        "resume_school_type": highest_school_type,
                        "requirement": requirement
                    }
                else:
                    reason_suffix = ""
                    if requires_fulltime and not matched_fulltime:
                        reason_suffix = f"（不满足全日制要求：简历为{highest_education_form if highest_education_form else '非全日制'}，岗位要求全日制）"
                    return {
                        "matched": False,
                        "reason": f"学历不符合要求：简历{highest_edu}（{highest_school_type}）{reason_suffix}，岗位要求{requirement}",
                        "method": method,
                        "detail": detail,
                        "resume_education": highest_edu,
                        "resume_school_type": highest_school_type,
                        "requirement": requirement
                    }
            elif "原文" in requirement:
                # 只有原文，使用文本匹配（只使用最高学历相关字段）
                requirement_text = requirement["原文"]
                return self.match_education_rule_text(requirement_text, highest_edu, "", 
                                                       highest_school_type, "", highest_education_form)
        
        # 默认处理
        method = "规则匹配-默认通过"
        logger.warning(f"学历筛选：{method}，要求格式无法识别")
        return {
            "matched": True,
            "reason": "学历要求格式无法识别，默认通过",
            "method": method,
            "detail": "要求格式无法识别，默认通过",
            "requirement": requirement
        }
    
    def match_education_rule_text(self, requirement_text: str, highest_edu: str, fulltime_edu: str,
                                  highest_school_type: str, fulltime_school_type: str,
                                  highest_education_form: str = "") -> Dict:
        """匹配学历规则（文本格式）"""
        edu_levels = {
            "博士": 5,
            "硕士研究生": 4,
            "硕士": 4,
            "大学本科": 3,
            "本科": 3,
            "专科": 2,
            "高中": 1
        }
        
        # 提取要求中的学历等级
        req_level = 0
        for edu, level in edu_levels.items():
            if edu in requirement_text:
                req_level = max(req_level, level)
        
        # 提取简历中的学历等级（只使用最高学历）
        resume_level = 0
        for edu, level in edu_levels.items():
            if edu in highest_edu:
                resume_level = max(resume_level, level)
        
        # 检查985/211要求（只使用最高学历毕业院校类型）
        has_985_211_req = "985" in requirement_text or "211" in requirement_text
        has_985_211_resume = "985" in highest_school_type or "211" in highest_school_type
        
        # 检查全日制要求
        requires_fulltime = "全日制" in requirement_text
        matched_fulltime = True  # 默认匹配（如果没有全日制要求）
        if requires_fulltime:
            # 如果岗位要求全日制，简历必须是全日制
            if highest_education_form == "全日制教育":
                matched_fulltime = True
            elif highest_education_form == "非全日制教育" or "非全日制" in highest_education_form:
                matched_fulltime = False
            else:
                # 如果学习形式字段为空，默认不匹配（严格模式）
                matched_fulltime = False
        
        detail_parts = []
        if has_985_211_req:
            matched = (has_985_211_resume or resume_level >= req_level) and matched_fulltime
            detail_parts.append(f"985/211要求：{'匹配' if has_985_211_resume else '不匹配'}")
        else:
            matched = resume_level >= req_level and matched_fulltime
        
        detail_parts.append(f"学历等级：简历{resume_level}级，要求≥{req_level}级")
        if requires_fulltime:
            detail_parts.append(f"学习形式：{'满足' if matched_fulltime else '不满足'}全日制要求（简历：{highest_education_form if highest_education_form else '未明确'}）")
        detail = "；".join(detail_parts)
        
        if matched:
            return {
                "matched": True,
                "reason": f"学历符合要求：简历{highest_edu}（{highest_school_type}），岗位要求{requirement_text}",
                "method": "规则匹配-文本解析",
                "detail": detail,
                "resume_education": highest_edu,
                "resume_school_type": highest_school_type,
                "requirement": requirement_text
            }
        else:
            return {
                "matched": False,
                "reason": f"学历不符合要求：简历{highest_edu}（{highest_school_type}），岗位要求{requirement_text}",
                "method": "规则匹配-文本解析",
                "detail": detail,
                "resume_education": highest_edu,
                "resume_school_type": highest_school_type,
                "requirement": requirement_text
            }
    
    def match_major_rule(self, requirement, major_names: List[str], major_classes: List[str], work_experience: List) -> Dict:
        """
        匹配专业规则（使用专业类匹配）
        
        Args:
            requirement: 岗位专业要求
            major_names: 简历专业名称列表
            major_classes: 简历专业对应的专业类名称列表
            work_experience: 工作经历列表
        
        Returns:
            匹配结果字典，包含matched、reason、need_llm等字段
        """
        method = "规则匹配-结构化数据"
        
        # 处理规整后的结构化数据
        if isinstance(requirement, dict):
            if "条件" in requirement and "专业" in requirement:
                # 规整后格式：{"条件":"或","专业":[...],"经历":[...]}
                condition = requirement.get("条件", "或")  # 条件为空时默认为"或"
                if not condition or condition == "":
                    condition = "或"
                
                required_majors = requirement.get("专业", [])  # 岗位要求的专业类列表
                experiences = requirement.get("经历", [])
                
                method = f"规则匹配-结构化数据（条件：{condition}）"
                logger.debug(f"专业筛选：使用{method}，专业要求={required_majors}，经历要求={experiences}")
                
                # 检查专业类匹配：简历的专业类是否在岗位要求的专业类列表中存在
                major_matched = False
                matched_classes = []
                for req_major in required_majors:
                    if isinstance(req_major, str):
                        # 移除"类"和"相关专业"后缀，获取专业类名称
                        req_major_clean = req_major.replace("类", "").replace("相关专业", "").strip()
                        # 检查简历的专业类是否包含这个专业类
                        for resume_class in major_classes:
                            # 移除"类"后缀进行比较
                            resume_class_clean = resume_class.replace("类", "").strip()
                            if req_major_clean == resume_class_clean or req_major_clean in resume_class_clean or resume_class_clean in req_major_clean:
                                major_matched = True
                                matched_classes.append(req_major)
                                break
                        if major_matched:
                            break
                
                # 检查工作经历匹配（如果有经历要求）
                experience_matched = False
                if experiences:
                    # 这里可以进一步检查工作经历
                    experience_matched = True  # 简化处理
                
                # 判断：根据条件类型
                if condition == "或":
                    matched = major_matched or experience_matched
                    match_detail = f"满足任一条件：专业匹配={major_matched}（匹配的专业类：{matched_classes}），经历匹配={experience_matched}"
                else:  # "与"条件
                    matched = major_matched and experience_matched
                    match_detail = f"满足所有条件：专业匹配={major_matched}（匹配的专业类：{matched_classes}），经历匹配={experience_matched}"
                
                logger.debug(f"专业筛选结果：{match_detail}")
                
                if matched:
                    return {
                        "matched": True,
                        "reason": f"专业符合要求：简历专业={major_names}，专业类={major_classes}，岗位要求={required_majors}",
                        "method": method,
                        "detail": match_detail,
                        "resume_majors": major_names,
                        "resume_major_classes": major_classes,
                        "requirement": requirement,
                        "need_llm": False
                    }
                else:
                    # 如果专业类不匹配，且没有经历要求或经历也不匹配，需要LLM判断
                    need_llm = not major_matched and (not experiences or not experience_matched)
                    return {
                        "matched": False,
                        "reason": f"专业不符合要求：简历专业={major_names}，专业类={major_classes}，岗位要求={required_majors}",
                        "method": method,
                        "detail": match_detail,
                        "resume_majors": major_names,
                        "resume_major_classes": major_classes,
                        "requirement": requirement,
                        "need_llm": need_llm
                    }
            elif "原文" in requirement:
                # 只有原文，使用文本匹配（保留原有逻辑）
                method = "规则匹配-文本解析"
                requirement_text = requirement["原文"]
                logger.debug(f"专业筛选：使用{method}，原文={requirement_text}")
                # 使用第一个专业名称进行文本匹配（兼容旧逻辑）
                major = major_names[0] if major_names else ""
                result = self.match_major_rule_text(requirement_text, major, work_experience)
                result["method"] = method
                result["need_llm"] = False
                return result
        
        # 默认处理
        method = "规则匹配-默认通过"
        logger.warning(f"专业筛选：{method}，要求格式无法识别")
        return {
            "matched": True,
            "reason": "专业要求格式无法识别，默认通过",
            "method": method,
            "requirement": requirement,
            "need_llm": False
        }
    
    def match_major_rule_text(self, requirement_text: str, major: str, work_experience: List) -> Dict:
        """匹配专业规则（文本格式）"""
        # 提取专业关键词
        major_keywords = re.findall(r"([^，,、]+?)(?:类|相关专业)", requirement_text)
        
        # 检查专业匹配
        matched = False
        reason = ""
        matched_keyword = ""
        
        for keyword in major_keywords:
            keyword_clean = keyword.strip()
            if keyword_clean in major or major in keyword_clean:
                matched = True
                matched_keyword = keyword_clean
                reason = f"专业匹配：简历专业{major}，岗位要求{keyword_clean}"
                break
        
        # 如果专业不匹配，检查是否有相关工作经历
        if not matched:
            reason = f"专业不匹配：简历专业{major}，岗位要求{requirement_text}"
        
        detail = f"关键词匹配：简历专业={major}，匹配关键词={matched_keyword if matched else '无'}"
        
        return {
            "matched": matched,
            "reason": reason,
            "method": "规则匹配-文本解析",
            "detail": detail,
            "resume_major": major,
            "requirement": requirement_text
        }
    
    def match_age_rule(self, requirement: Dict, age: int) -> Dict:
        """匹配年龄规则"""
        max_age = requirement.get("max_age")
        method = "规则匹配-数值比较"
        detail = f"年龄计算：{age}岁，要求≤{max_age}岁"
        
        logger.debug(f"年龄匹配：{detail}")
        
        if age <= max_age:
            return {
                "matched": True,
                "reason": f"年龄符合要求：{age}岁，不超过{max_age}周岁",
                "method": method,
                "detail": detail,
                "age": age,
                "max_age": max_age
            }
        else:
            return {
                "matched": False,
                "reason": f"年龄不符合要求：{age}岁，超过{max_age}周岁",
                "method": method,
                "detail": detail,
                "age": age,
                "max_age": max_age
            }
    
    def match_performance_rule(self, requirement, resume_data: Dict) -> Dict:
        """匹配绩效规则（规则方式）"""
        method = "规则匹配-数据缺失"
        
        # 检查简历中是否有绩效信息
        performance_data = resume_data.get("年度绩效情况", {})
        has_performance_info = performance_data and isinstance(performance_data, dict) and len(performance_data) > 0
        
        # 如果简历中没有绩效信息，但岗位有绩效要求，判定为不通过
        if not has_performance_info:
            logger.debug("绩效筛选：岗位有绩效要求，但简历中无绩效信息，判定为不通过")
            return {
                "matched": False,
                "reason": "岗位要求绩效，但简历中无绩效信息，不符合要求",
                "method": method,
                "detail": "简历中无绩效信息，无法通过规则判断",
                "requirement": requirement
            }
        
        # 处理新格式的规整后数据
        if isinstance(requirement, dict):
            if "条件" in requirement and "系统内" in requirement:
                # 新格式：{"条件":"与","系统内":"...","系统外":"..."}
                # 需要根据系统内外判断，但简历中无明确信息，判定为不通过
                method = "规则匹配-系统内外判断（数据缺失）"
                logger.debug("绩效筛选：需要根据系统内外判断，但简历中无明确信息")
                return {
                    "matched": False,
                    "reason": "绩效要求需要根据系统内外判断，但简历中无明确信息，不符合要求",
                    "method": method,
                    "detail": "简历中无绩效信息，无法通过规则判断",
                    "requirement": requirement
                }
        
        # 如果有绩效信息，但无法通过规则判断，应该使用LLM（这里不应该到达）
        logger.debug("绩效筛选：有绩效信息，但无法通过规则判断，应使用LLM")
        return {
            "matched": True,
            "reason": "简历中有绩效信息，但需要LLM判断",
            "method": method,
            "detail": "需要LLM判断",
            "requirement": requirement
        }
    
    def match_work_experience_rule(self, requirement, work_experience: List, join_date: str, basic_info: Dict) -> Dict:
        """匹配工作经历规则"""
        method = "规则匹配-系统内外判断（数据缺失）"
        
        # 处理新格式的规整后数据
        if isinstance(requirement, dict):
            if "条件" in requirement:
                # 新格式：{"条件":"或","南方电网公司系统内应聘人员":"...","南方电网公司系统外应聘人员":"..."}
                condition = requirement.get("条件", "或")
                system_in = requirement.get("南方电网公司系统内应聘人员", "")
                system_out = requirement.get("南方电网公司系统外应聘人员", "")
                
                logger.debug(f"工作经历筛选：需要根据系统内外判断（条件：{condition}），但无法确定简历是系统内还是系统外")
                return {
                    "matched": True,
                    "reason": "工作经历要求需要根据系统内外判断，默认通过",
                    "method": method,
                    "detail": "无法确定简历是系统内还是系统外，默认通过",
                    "requirement": requirement
                }
            elif "原文" in requirement:
                method = "规则匹配-文本解析（简化）"
                logger.debug("工作经历筛选：使用原文，简化判断")
                return {
                    "matched": True,
                    "reason": "工作经历符合要求（规则判断）",
                    "method": method,
                    "detail": "使用原文进行简化判断",
                    "requirement": requirement["原文"]
                }
        
        # 简化实现
        logger.debug("工作经历筛选：简化判断，默认通过")
        return {
            "matched": True,
            "reason": "工作经历符合要求（规则判断）",
            "method": method,
            "detail": "简化判断，默认通过",
            "requirement": requirement
        }
    
    def match_work_years_rule(self, requirement: Dict, work_experience: List, join_date: str) -> Dict:
        """匹配工作经验年数规则"""
        method = "规则匹配-数值比较"
        
        # 从requirement中提取最低年限要求
        min_years = 0
        
        # 支持多种数据格式
        if isinstance(requirement, dict):
            # 格式1：{"min_years": 3}
            if "min_years" in requirement:
                min_years = requirement.get("min_years", 0)
            # 格式2：{"规整后": "≥3"} 或 {"规整后": "3"}
            elif "规整后" in requirement:
                normalized = requirement.get("规整后", "")
                if normalized:
                    # 解析 "≥3" 或 "3" 格式
                    import re
                    match = re.search(r'(\d+)', str(normalized))
                    if match:
                        min_years = int(match.group(1))
                        logger.debug(f"工作经验筛选：从规整后提取年限要求={min_years}年，原值={normalized}")
        
        # 如果没有提取到年限要求，默认通过
        if min_years == 0:
            logger.debug("工作经验筛选：未提取到年限要求，默认通过")
            return {
                "matched": True,
                "reason": "岗位未明确工作年限要求",
                "method": "规则匹配-无要求",
                "detail": "岗位未明确工作年限要求",
                "min_years": 0
            }
        
        # 计算工作年限
        if join_date:
            years = self.calculator.calculate_work_years(join_date)
            detail = f"工作年限计算：参加工作时间={join_date}，计算年限={years}年，要求≥{min_years}年"
            logger.debug(f"工作经验筛选：{detail}")
            
            if years >= min_years:
                return {
                    "matched": True,
                    "reason": f"工作年限符合要求：{years}年，要求{min_years}年及以上",
                    "method": method,
                    "detail": detail,
                    "work_years": years,
                    "min_years": min_years
                }
            else:
                return {
                    "matched": False,
                    "reason": f"工作年限不符合要求：{years}年，要求{min_years}年及以上",
                    "method": method,
                    "detail": detail,
                    "work_years": years,
                    "min_years": min_years
                }
        else:
            logger.warning("工作经验筛选：简历中缺少参加工作时间信息")
            return {
                "matched": False,
                "reason": "简历中缺少参加工作时间信息",
                "method": method,
                "detail": "数据缺失：缺少参加工作时间",
                "min_years": min_years
            }
    
    def match_political_rule(self, requirement: str, political_status: str) -> Dict:
        """匹配政治面貌规则"""
        method = "规则匹配-无要求"
        logger.debug(f"政治面貌筛选：岗位未明确要求，简历政治面貌={political_status}")
        return {
            "matched": True,
            "reason": "岗位未明确政治面貌要求",
            "method": method,
            "detail": "",
            "political_status": political_status
        }
    
    def match_title_rule(self, requirement, resume_data: Dict) -> Dict:
        """匹配职称规则（规则方式）"""
        method = "规则匹配-数据缺失"
        
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
        
        # 如果简历中没有职称信息，但岗位有职称要求，判定为不通过
        if not has_title_info:
            logger.debug(f"职称筛选：岗位有职称要求={requirement}，但简历中无职称信息，判定为不通过")
            requirement_text = ""
            if isinstance(requirement, list):
                requirement_text = "、".join(requirement)
            elif isinstance(requirement, dict) and "原文" in requirement:
                requirement_text = requirement["原文"]
            else:
                requirement_text = str(requirement)
            
            return {
                "matched": False,
                "reason": f"岗位要求职称（{requirement_text}），但简历中无职称信息，不符合要求",
                "method": method,
                "detail": "简历中无职称信息，无法通过规则判断",
                "requirement": requirement
            }
        
        # 如果有职称信息，但无法通过规则判断，应该使用LLM（这里不应该到达）
        logger.debug("职称筛选：有职称信息，但无法通过规则判断，应使用LLM")
        return {
            "matched": True,
            "reason": "简历中有职称信息，但需要LLM判断",
            "method": method,
            "detail": "需要LLM判断",
            "requirement": requirement
        }
