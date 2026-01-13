import pandas as pd
import json

def excel_to_title_json(excel_path, sheet_name="职称库", output_path="output/03_职称库.json"):
    """
    将 Excel 中 '职称库' sheet 转换为扁平分组的 JSON 格式。
    
    Args:
        excel_path (str): Excel 文件路径
        sheet_name (str): 工作表名称，默认为 "职称库"
        output_path (str): 输出 JSON 文件路径
    """
    # 读取Excel文件中的指定sheet
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=0)

    # 确保列名正确（自动去除空格）
    df.columns = df.columns.str.strip()
    required_columns = ["职称名称", "职称等级", "别名"]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Excel文件必须包含列: {required_columns}")

    # 填充缺失值为空字符串（便于后续处理）
    df = df.fillna("")

    # === 新增：统计原始数据条数 ===
    total_records = len(df)
    total_titles = df["职称名称"].nunique()
    print(f"📊 数据统计:")
    print(f"   - 职称名称种类数: {total_titles}")
    print(f"   - 原始记录总条数: {total_records}")

    # 构建分组结构（关键：groupby 设置 sort=False 以保持原始顺序）
    result = {"职称库列表": []}
    grouped_by_title = df.groupby("职称名称", sort=False)  # 保持职称在Excel中的首次出现顺序

    for title_name, group in grouped_by_title:
        # 获取该职称下所有“职称等级”，保持原始行顺序
        levels = group["职称等级"].astype(str).tolist()
        # 别名字段：原始数据为空，统一设为 ""
        alias = ""

        result["职称库列表"].append({
            "职称名称": str(title_name).strip(),
            "职称等级": levels,
            "别名": alias
        })

    # 写入JSON文件（UTF-8编码，中文不转义）
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 转换完成！结果已保存至: {output_path}")


if __name__ == "__main__":
    # 修改为你实际的文件路径（如果脚本和文件在同一目录）
    excel_file = "主题库数据.xlsx"
    excel_to_title_json(excel_file)