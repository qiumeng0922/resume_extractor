import pandas as pd
import json

def excel_to_computer_level_json(excel_path, sheet_name="计算机水平库", output_path="output/02_计算机水平库.json"):
    """
    将 Excel 中 '计算机水平库' sheet 转换为分组 JSON 格式。
    
    Args:
        excel_path (str): Excel 文件路径
        sheet_name (str): 工作表名称，默认为 "计算机水平库"
        output_path (str): 输出 JSON 文件路径
    """
    # 读取Excel文件中的指定sheet
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=0)

    # 确保列名正确（自动去除空格）
    df.columns = df.columns.str.strip()
    required_columns = ["级别", "科目名称", "入库时间", "版本"]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Excel文件必须包含列: {required_columns}")

    # 填充缺失值为空字符串（便于后续处理）
    df = df.fillna("")

    # === 新增：统计原始数据条数 ===
    total_records = len(df)
    total_levels = df["级别"].nunique()
    print(f"📊 数据统计:")
    print(f"   - 级别数量: {total_levels}")
    print(f"   - 科目总条数: {total_records}")

    # 构建分组结构（关键：groupby 设置 sort=False 以保持原始顺序）
    result = {"计算机水平库列表": []}
    grouped_by_level = df.groupby("级别", sort=False)  # 保持级别在Excel中的首次出现顺序

    for level, group in grouped_by_level:
        # 获取该级别下所有“科目名称”，保持原始行顺序
        subjects = group["科目名称"].astype(str).tolist()

        result["计算机水平库列表"].append({
            "级别": str(level).strip(),
            "职称等级": subjects,  # 注意：虽然字段叫“职称等级”，但实际是科目名称列表（按你给的模板）
            "入库时间": "",
            "版本": ""
        })

    # 写入JSON文件（UTF-8编码，中文不转义）
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 转换完成！结果已保存至: {output_path}")


if __name__ == "__main__":
    # 修改为你实际的文件路径（如果脚本和文件在同一目录）
    excel_file = "主题库数据.xlsx"
    excel_to_computer_level_json(excel_file)