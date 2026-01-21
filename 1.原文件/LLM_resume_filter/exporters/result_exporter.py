#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结果导出器模块
"""

import json
from typing import Dict, List
from datetime import datetime
from utils.logger_config import setup_logger
from core.models import ScreeningResult

logger = setup_logger("result_exporter")


def export_screening_results(all_results: List[ScreeningResult], jobs: List[Dict], resumes: List[Dict], output_file: str = "筛选结果.json"):
    """
    导出筛选结果为JSON格式
    
    Args:
        all_results: 所有筛选结果
        jobs: 岗位列表
        resumes: 所有简历列表
        output_file: 输出文件名
    """
    # 构建输出结果列表（每个简历一条记录，参考简历初筛结果.json格式）
    output_list = []
    
    # 为每个筛选结果创建一条记录
    for result in all_results:
        resume_id = result.resume_id
        
        # 从resumes列表中查找简历数据
        resume_data = None
        for resume in resumes:
            if str(resume.get('序号', '')) == resume_id:
                resume_data = resume
                break
        
        if not resume_data:
            continue
        
        # 获取基本信息
        basic_info = resume_data.get('基本信息', {})
        name = basic_info.get('姓名', '')
        resume_number = resume_data.get('序号', '')
        
        # 获取岗位信息
        job_info = resume_data.get('岗位信息', {})
        applied_position = job_info.get('应聘岗位', '')
        
        # 获取学习经历统计信息
        education_info = resume_data.get('学习经历统计信息', {})
        highest_education = education_info.get('最高学历', '')
        highest_school = education_info.get('最高学历毕业院校', '')
        highest_school_type = education_info.get('最高学历毕业院校类型', '')
        
        # 计算年龄
        birth_date = basic_info.get('出生日期', '')
        age = ''
        if birth_date:
            try:
                date_part = birth_date.split()[0] if ' ' in birth_date else birth_date
                parts = date_part.split('-')
                if len(parts) >= 1:
                    year = int(parts[0])
                    month = int(parts[1]) if len(parts) > 1 else 1
                    day = int(parts[2]) if len(parts) > 2 else 1
                    current_date = datetime.now()
                    age_calc = current_date.year - year
                    if (current_date.month, current_date.day) < (month, day):
                        age_calc -= 1
                    age = str(age_calc)
            except:
                pass
        
        # 构建关键画像
        key_profile_parts = []
        if highest_education:
            key_profile_parts.append(highest_education)
        if highest_school:
            key_profile_parts.append(highest_school)
        if highest_school_type:
            key_profile_parts.append(highest_school_type)
        if age:
            key_profile_parts.append(f"{age}岁")
        
        key_profile = ' | '.join(key_profile_parts) if key_profile_parts else ''
        
        # 获取现职务或岗位
        current_position = basic_info.get('现职务或岗位', '')
        if current_position:
            key_profile += f"\n现任：{current_position}"
        
        # 构建AI初筛结果
        ai_result = "拟通过" if result.passed else "拟淘汰"
        
        # 构建淘汰原因（未通过的筛选条件）
        failed_filters = [detail.get('filter_name') for detail in result.filter_details if not detail.get('passed')]
        elimination_reason = '/'.join(failed_filters) if failed_filters else ''
        
        # 构建筛选条件详情
        filter_details = []
        for detail in result.filter_details:
            filter_name = detail.get('filter_name', '')
            passed = detail.get('passed', False)
            method = detail.get('method', detail.get('source', '未知'))
            reason = detail.get('reason', '')
            
            # 获取筛选详情
            detail_info = detail.get('details', {})
            detail_text = ''
            if isinstance(detail_info, dict):
                detail_text = detail_info.get('detail', '')
            
            # 转换判断方法：'rule' -> '规则', 'llm' -> 'LLM'
            if method == 'rule' or '规则' in str(method):
                method_display = '规则'
            elif method == 'llm' or 'LLM' in str(method):
                method_display = 'LLM'
            else:
                method_display = str(method)
            
            filter_detail = {
                "筛选条件": filter_name,
                "是否通过": "通过" if passed else "不通过",
                "判断方法": method_display,
                "原因说明": reason,
                "筛选详情": detail_text
            }
            filter_details.append(filter_detail)
        
        # 构建输出记录
        output_record = {
            "序号": int(resume_number) if str(resume_number).isdigit() else resume_number,
            "姓名": name,
            "关键画像": key_profile,
            "应聘岗位": applied_position,
            "AI初筛结果": ai_result,
            "淘汰原因": elimination_reason,
            "筛选条件详情": filter_details
        }
        
        output_list.append(output_record)
    
    # 按序号排序
    output_list.sort(key=lambda x: x.get('序号', 0) if isinstance(x.get('序号'), (int, str)) and str(x.get('序号')).isdigit() else 0)
    
    # 保存到文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_list, f, ensure_ascii=False, indent=2)
    
    logger.info(f"筛选结果已导出到：{output_file}")
    print(f"\n✅ 筛选结果已导出到：{output_file}")
