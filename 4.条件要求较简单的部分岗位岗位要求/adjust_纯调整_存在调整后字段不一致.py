# -*- coding: utf-8 -*-
"""
JSON 规整工具
功能：根据"原文"字段提取结构化信息填充到"规整后"字段

重要特性：
1. ✅ 不改变原始 JSON 结构 - 只填充"规整后"字段
2. ✅ 如果"原文"为空，"规整后"也保持为空
3. ✅ 对于不同格式的记录，保持原样不处理
4. ✅ 完全保留原始数据的完整性
"""

import json
import re
import os


def extract_condition_type(text):
    """
    提取条件类型：或/且
    """
    if not text:
        return ""
    
    # 判断"或"条件
    or_keywords = ["任一", "或", "可选"]
    for keyword in or_keywords:
        if keyword in text:
            return "或"
    
    # 判断"且"条件
    and_keywords = ["且", "同时", "并"]
    for keyword in and_keywords:
        if keyword in text:
            return "且"
    
    return ""


def process_education_requirement(original_text):
    """
    处理学历要求
    返回: {"条件": "", "排名": [], "学历": []}
    """
    if not original_text or not original_text.strip():
        return {"条件": "", "排名": [], "学历": []}
    
    result = {
        "条件": extract_condition_type(original_text),
        "排名": [],
        "学历": []
    }
    
  # 按①②或标点分割
    sentences = re.split(r'[①②③④⑤⑥⑦⑧⑨⑩]|[，。；]', original_text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # 判断是否包含排行榜关键词（不包括985/211，它们应该放入学历）
        has_ranking = any(keyword in sentence for keyword in ["排行榜", "QS", "泰晤士"])
        
        if has_ranking:
            result["排名"].append(sentence)
        elif any(keyword in sentence for keyword in ["985", "211", "双一流", "学历", "学位", "本科", "硕士", "博士"]):
            result["学历"].append(sentence)
    
    return result


def process_major_requirement(original_text):
    """
    处理专业要求
    返回: {"条件": "", "专业": [], "经历": []}
    """
    if not original_text or not original_text.strip():
        return {"条件": "", "专业": [], "经历": []}
    
    result = {
        "条件": extract_condition_type(original_text),
        "专业": [],
        "经历": []
    }
    
    # 分离专业和经历
    parts = re.split(r'[。]', original_text)
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        # 判断是否是经历描述
        if "具备" in part or "工作经历" in part or "年" in part and "专业" not in part:
            result["经历"].append(part + "。" if not part.endswith("。") else part)
        else:
            # 按逗号分割专业
            majors = re.split(r'[，,]', part)
            for major in majors:
                major = major.strip()
                if major and major not in ["或"]:
                    result["专业"].append(major)
    
    return result


def process_age_requirement(original_text):
    """
    处理年龄要求
    返回: "" (字符串格式，如 "≤40")
    """
    if not original_text or not original_text.strip():
        return ""
    
    # 提取数字
    numbers = re.findall(r'\d+', original_text)
    if not numbers:
        return ""
    
    age = numbers[0]
    
    # 判断比较关系
    if "不超过" in original_text or "以下（含）" in original_text:
        return f"≤{age}"
    elif "以下" in original_text:
        return f"<{age}"
    elif "及以上" in original_text or "不少于" in original_text:
        return f"≥{age}"
    elif "以上" in original_text:
        return f">{age}"
    elif len(numbers) >= 2:
        return f"{numbers[0]}-{numbers[1]}"
    
    return f"≤{age}"


def process_performance_requirement(original_text):
    """
    处理绩效要求
    返回: {"条件": "", "系统内": "", "系统外": ""}
    """
    if not original_text or not original_text.strip():
        return {"条件": "", "系统内": "", "系统外": ""}
    
    result = {
        "条件": "",
        "系统内": "",
        "系统外": ""
    }
    
    # 判断是否同时包含系统内和系统外
    if "系统内" in original_text and "系统外" in original_text:
        result["条件"] = "与"
        
        # 分割系统内和系统外
        parts = original_text.split("系统外")
        if len(parts) == 2:
            # 提取系统内部分
            system_in_part = parts[0]
            if "系统内" in system_in_part:
                system_in_text = system_in_part.split("系统内")[-1].strip()
                # 移除开头的逗号或顿号
                system_in_text = re.sub(r'^[，,、]', '', system_in_text)
                result["系统内"] = system_in_text
            
            # 提取系统外部分
            system_out_text = parts[1].strip()
            # 移除开头的逗号或顿号
            system_out_text = re.sub(r'^[，,、]', '', system_out_text)
            result["系统外"] = system_out_text
    
    return result


def process_title_requirement(original_text):
    """
    处理职称要求
    返回: [] (数组)
    """
    if not original_text or not original_text.strip():
        return []
    
    result = []
    
    # 职称等级映射
    if "正高级" in original_text:
        result.append("正高级")
    
    if "副高级" in original_text or ("高级" in original_text and "副高级" not in result):
        if "副高级" not in result:
            result.append("副高级")
    
    if "中级" in original_text:
        result.append("中级")
    
    if "初级" in original_text:
        result.append("初级")
    
    # 处理"及以上"的情况
    if "高级及以上" in original_text or "副高级及以上" in original_text:
        result = ["正高级", "副高级"]
    elif "中级及以上" in original_text:
        result = ["正高级", "副高级", "中级"]
    
    return result


def process_work_experience_qualification(original_text):
    """
    处理资格条件中的工作经历
    返回: {"条件": "", "南方电网公司系统内应聘人员": "", "南方电网公司系统外应聘人员": ""}
    """
    if not original_text or not original_text.strip():
        return {"条件": "", "南方电网公司系统内应聘人员": "", "南方电网公司系统外应聘人员": ""}
    
    result = {
        "条件": "",
        "南方电网公司系统内应聘人员": "",
        "南方电网公司系统外应聘人员": ""
    }
    
    # 判断是否有（1）和（2）标记
    if "（1）" in original_text and "（2）" in original_text:
        result["条件"] = "或"
        
        # 分割（1）和（2）
        parts = original_text.split("（2）")
        if len(parts) == 2:
            # 提取（1）部分
            part1 = parts[0]
            if "（1）" in part1:
                part1_text = part1.split("（1）")[-1].strip()
                # 提取系统内应聘人员后的内容
                if "系统内应聘人员" in part1_text or "南方电网公司系统内应聘人员" in part1_text:
                    system_in_text = re.split(r'系统内应聘人员[:：]', part1_text)[-1].strip()
                    result["南方电网公司系统内应聘人员"] = system_in_text
            
            # 提取（2）部分
            part2_text = parts[1].strip()
            # 提取系统外应聘人员后的内容
            if "系统外应聘人员" in part2_text or "南方电网公司系统外应聘人员" in part2_text:
                system_out_text = re.split(r'系统外应聘人员[:：]', part2_text)[-1].strip()
                result["南方电网公司系统外应聘人员"] = system_out_text
    
    return result


def process_work_experience_position(original_text):
    """
    处理岗位任职条件中的工作经验
    返回: "" (字符串格式，如 "≥3")
    """
    if not original_text or not original_text.strip():
        return ""
    
    # 提取数字
    numbers = re.findall(r'\d+', original_text)
    if not numbers:
        return ""
    
    years = numbers[0]
    
    # 判断比较关系
    if "及以上" in original_text or "以上" in original_text or "不少于" in original_text:
        return f"≥{years}"
    elif "以上" in original_text:
        return f">{years}"
    elif len(numbers) >= 2:
        return f"{numbers[0]}-{numbers[1]}"
    
    return f"≥{years}"


def process_certificate_requirement(original_text):
    """
    处理持证要求
    返回: "" (直接返回原文)
    """
    if not original_text:
        return ""
    return original_text.strip()


def adjust_qualification_conditions(qualification_conditions):
    """
    调整资格条件的规整后字段
    不改变原始JSON结构，只填充规整后字段
    """
    if not isinstance(qualification_conditions, list):
        return
    
    for condition_group in qualification_conditions:
        if not isinstance(condition_group, dict):
            continue
            
        for field_name, field_data in condition_group.items():
            if not isinstance(field_data, list) or len(field_data) < 2:
                continue
            
            # 获取原文
            original = ""
            for item in field_data:
                if isinstance(item, dict) and "原文" in item:
                    original = item["原文"]
                    break
            
            # 根据字段类型处理
            if field_name == "学历要求":
                adjusted = process_education_requirement(original)
                for item in field_data:
                    if isinstance(item, dict) and "规整后" in item:
                        item["规整后"] = adjusted
                        
            elif field_name == "专业要求":
                adjusted = process_major_requirement(original)
                for item in field_data:
                    if isinstance(item, dict) and "规整后" in item:
                        item["规整后"] = adjusted
                        
            elif field_name == "年龄要求":
                adjusted = process_age_requirement(original)
                for item in field_data:
                    if isinstance(item, dict) and "规整后" in item:
                        item["规整后"] = adjusted
                        
            elif field_name == "绩效要求":
                adjusted = process_performance_requirement(original)
                for item in field_data:
                    if isinstance(item, dict) and "规整后" in item:
                        item["规整后"] = adjusted
                        
            elif field_name == "职称要求":
                adjusted = process_title_requirement(original)
                for item in field_data:
                    if isinstance(item, dict) and "规整后" in item:
                        item["规整后"] = adjusted
                        
            elif field_name == "工作经历":
                adjusted = process_work_experience_qualification(original)
                for item in field_data:
                    if isinstance(item, dict) and "规整后" in item:
                        item["规整后"] = adjusted


def adjust_position_requirements(position_requirements):
    """
    调整岗位任职条件的规整后字段
    不改变原始JSON结构，只填充规整后字段
    """
    # 检查是否是字典数组格式
    if not isinstance(position_requirements, list):
        return
    
    # 如果数组中全是字符串，说明格式不同，直接返回不处理
    if all(isinstance(item, str) for item in position_requirements):
        return
    
    for requirement_group in position_requirements:
        # 检查是否是字典
        if not isinstance(requirement_group, dict):
            continue
            
        for field_name, field_data in requirement_group.items():
            # 能力要求是数组，不需要处理规整后
            if field_name == "能力要求":
                continue
            
            if not isinstance(field_data, list) or len(field_data) < 2:
                continue
            
            # 获取原文
            original = ""
            for item in field_data:
                if isinstance(item, dict) and "原文" in item:
                    original = item["原文"]
                    break
            
            # 根据字段类型处理
            if field_name == "工作经验":
                adjusted = process_work_experience_position(original)
                for item in field_data:
                    if isinstance(item, dict) and "规整后" in item:
                        item["规整后"] = adjusted
                        
            elif field_name == "持证要求":
                adjusted = process_certificate_requirement(original)
                for item in field_data:
                    if isinstance(item, dict) and "规整后" in item:
                        item["规整后"] = adjusted


def adjust_json_file(input_file, output_file):
    """
    调整 JSON 文件中的规整后字段
    """
    print("=" * 80)
    print("🔧 JSON 规整工具")
    print("=" * 80)
    print(f"📁 输入文件: {input_file}")
    print(f"💾 输出文件: {output_file}")
    print()
    
    # 读取 JSON 文件
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ 成功读取 JSON 文件")
        print(f"📊 记录数: {len(data)}")
        print()
        
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return
    
    # 处理每条记录
    print("⏳ 正在处理数据...")
    for idx, record in enumerate(data, 1):
        # 处理资格条件
        if "资格条件" in record and isinstance(record["资格条件"], list):
            adjust_qualification_conditions(record["资格条件"])
        
        # 处理岗位任职条件
        if "岗位任职条件" in record and isinstance(record["岗位任职条件"], list):
            adjust_position_requirements(record["岗位任职条件"])
        
        if idx % 5 == 0:
            print(f"   已处理 {idx}/{len(data)} 条记录...")
    
    print(f"✅ 数据处理完成！")
    print()
    
    # 写入输出文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 成功写入输出文件")
        print(f"💾 输出路径: {output_file}")
        print()
        print("=" * 80)
        print("🎉 任务完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ 写入文件失败: {e}")


if __name__ == "__main__":
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 定义输入输出文件路径
    input_file = os.path.join(current_dir, "条件要求较简单的部分岗位岗位要求-模拟数据.json")
    output_file = os.path.join(current_dir, "条件要求较简单的部分岗位岗位要求-模拟数据_规整后不统一.json")
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"❌ 输入文件不存在: {input_file}")
        exit(1)
    
    # 执行调整
    adjust_json_file(input_file, output_file)

