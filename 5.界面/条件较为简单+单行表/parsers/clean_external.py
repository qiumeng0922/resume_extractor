'''
对岗位转为josn后面,去除系统外的数据
'''
import json
import re
import sys

def clean_text_remove_external(text: str) -> str:
    if not isinstance(text, str):
        return text

    # 1. 删除“系统外，...”短语
    text = re.sub(r'系统外[^。；]*[。；]?', '', text)

    # 2. 删除完整的（2）系统外应聘人员句
    text = re.sub(r'（2）南方电网公司系统外应聘人员.*?(?=[。；]|$)', '', text)

    # 3. 兜底：如果存在“（2）南方电网公司”且后面没有“系统内”，也删掉（防止残片）
    text = re.sub(r'（2）南方电网公司[^。；]*[。；]?', '', text)

    # 4. 清理结尾
    text = re.sub(r'[；。]+$', '', text)
    text = re.sub(r'（2）\s*$', '', text)
    text = text.strip()

    return text

def clean_dict_remove_external(obj):
    """递归清理字典/列表中的系统外内容（仅删除键名含‘系统外’的字段）"""
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if isinstance(k, str) and "系统外" in k:
                continue
            cleaned_v = clean_dict_remove_external(v)
            new_obj[k] = cleaned_v
        return new_obj
    elif isinstance(obj, list):
        return [clean_dict_remove_external(item) for item in obj]
    else:
        return obj

def post_process_qualifications(qual_list):
    """专门处理资格条件中的绩效要求和工作经历"""
    for item in qual_list:
        for key in item:
            sub_list = item[key]
            if not isinstance(sub_list, list):
                continue
            for entry in sub_list:
                # 处理“原文”
                if isinstance(entry, dict) and "原文" in entry:
                    orig = entry.get("原文", "")
                    if isinstance(orig, str):
                        entry["原文"] = clean_text_remove_external(orig)
                # 处理“规整后”
                if isinstance(entry, dict) and "规整后" in entry:
                    refined = entry["规整后"]
                    if isinstance(refined, dict):
                        refined.pop("系统外", None)
                        refined.pop("南方电网公司系统外应聘人员", None)
    return qual_list

def clean_position_data(input_data):
    """
    清理岗位数据中的系统外内容
    
    Args:
        input_data: 岗位数据列表（JSON格式的数据）
    
    Returns:
        清理后的岗位数据列表
    """
    cleaned_data = []
    for record in input_data:
        cleaned_record = clean_dict_remove_external(record)
        # 特殊处理资格条件
        if "资格条件" in cleaned_record:
            cleaned_record["资格条件"] = post_process_qualifications(cleaned_record["资格条件"])
        cleaned_data.append(cleaned_record)
    
    return cleaned_data


def main():
    """
    主函数：从命令行参数或默认值获取输入输出文件名
    用法：
        python clean_external.py [输入文件] [输出文件]
        如果不提供参数，则使用默认文件名
    """
    # 从命令行参数获取文件名
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        # 默认文件名（向后兼容）
        input_file = "./data/条件要求较简单的部分岗位岗位要求-模拟数据_规整后.json"
    
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # 如果没有指定输出文件，根据输入文件名自动生成
        if input_file.endswith(".json"):
            output_file = input_file.replace(".json", "_去掉系统外.json")
        else:
            output_file = input_file + "_去掉系统外.json"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
    except FileNotFoundError:
        print(f"错误：未找到输入文件 '{input_file}'")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误：JSON 格式不正确 - {e}")
        sys.exit(1)

    # 清理数据
    cleaned_data = clean_position_data(input_data)

    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    print(f"处理完成！结果已保存至：{output_file}")
    return cleaned_data

if __name__ == "__main__":
    main()