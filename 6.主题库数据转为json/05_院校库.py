import pandas as pd
import json
import re

def excel_to_university_json(excel_path, sheet_name="院校库", output_path="output/05_院校库.json"):
    # 读取Excel文件中的指定sheet
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=0)

    # 清理列名：去除前后空格
    df.columns = df.columns.str.strip()

    # 确保必要列存在
    required_columns = ["院校中文名称", "院校英文名称", "院校类型", "地区", "属性标签"]
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Excel文件缺少必要列: {missing_cols}")

    # 填充缺失值为空字符串
    df = df.fillna("")

    # 处理“属性标签”：支持中文顿号、英文逗号、空格等分隔符，分割成列表
    def parse_tags(tag_str):
        if not tag_str or not isinstance(tag_str, str):
            return []
        # 使用正则分割：匹配中文顿号、英文逗号、分号、空格等
        tags = re.split(r'[、,;\s]+', tag_str.strip())
        # 过滤空字符串并去重（保持顺序）
        seen = set()
        unique_tags = []
        for t in tags:
            t_clean = t.strip()
            if t_clean and t_clean not in seen:
                unique_tags.append(t_clean)
                seen.add(t_clean)
        return unique_tags

    # 构建结果列表
    university_list = []
    for _, row in df.iterrows():
        chinese_name = str(row["院校中文名称"]).strip() if row["院校中文名称"] else ""
        english_name = str(row["院校英文名称"]).strip() if row["院校英文名称"] else ""
        school_type = str(row["院校类型"]).strip() if row["院校类型"] else ""
        region = str(row["地区"]).strip() if row["地区"] else ""
        tags = parse_tags(row["属性标签"])

        university_list.append({
            "院校中文名称": chinese_name,
            "院校英文名称": english_name,
            "院校类型": school_type,
            "地区": region,
            "属性标签": tags
        })

    # 统计信息
    total_universities = len(university_list)
    境内_count = sum(1 for u in university_list if u["院校类型"] == "境内")
    境外_count = total_universities - 境内_count
    print(f"📊 数据统计:")
    print(f"   - 院校总数: {total_universities}")
    print(f"   - 境内院校: {境内_count}")
    print(f"   - 境外院校: {境外_count}")

    # 构造最终JSON结构
    result = {
        "院校库列表": university_list
    }

    # 写入JSON文件（UTF-8编码，中文不转义）
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 转换完成！结果已保存至: {output_path}")


if __name__ == "__main__":
    # 修改为你实际的文件路径（如果脚本和文件在同一目录）
    excel_file = "主题库数据.xlsx"
    excel_to_university_json(excel_file)