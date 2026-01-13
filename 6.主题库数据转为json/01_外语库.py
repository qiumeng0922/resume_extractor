import pandas as pd
import json

def excel_to_foreign_lang_json(excel_path, sheet_name="外语库", output_path="output/01_外语库.json"):
    """
    将 Excel 中 '外语库' sheet 转换为嵌套 JSON 格式。
    
    Args:
        excel_path (str): Excel 文件路径
        sheet_name (str): 工作表名称，默认为 "外语库"
        output_path (str): 输出 JSON 文件路径
    """
    # 读取Excel文件中的指定sheet
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=0)

    # 确保列名正确（自动去除空格）
    df.columns = df.columns.str.strip()
    required_columns = ["语言", "级别", "满分值", "合格值"]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Excel文件必须包含列: {required_columns}")

    # 填充缺失值为空字符串（便于后续处理）
    df = df.fillna("")

    # === 新增：统计原始数据条数 ===
    total_records = len(df)
    total_languages = df["语言"].nunique()
    print(f"📊 数据统计:")
    print(f"   - 语种数量: {total_languages}")
    print(f"   - 考试级别总条数: {total_records}")

    # 构建嵌套结构（关键：groupby 设置 sort=False 以保持原始顺序）
    result = {"外语库列表": []}
    grouped_by_language = df.groupby("语言", sort=False)  # 保持语言在Excel中的首次出现顺序

    for language, group in grouped_by_language:
        level_list = []
        # 遍历该语言下的每一行，保留原始顺序
        for _, row in group.iterrows():
            level_list.append({
                "级别": str(row["级别"]).strip(),
                "满分值": str(row["满分值"]).strip() if row["满分值"] != "" else "",
                "合格值": str(row["合格值"]).strip() if row["合格值"] != "" else "",
                "入库时间": str(row["入库时间"]).strip() if row["入库时间"] != "" else "",
                "版本": str(row["版本"]).strip() if row["版本"] != "" else "",
                "版本时间": str(row["版本时间"]).strip() if row["版本时间"] != "" else ""
            })
        
        result["外语库列表"].append({
            "语言": str(language).strip(),
            "级别列表": level_list
        })

    # 写入JSON文件（UTF-8编码，中文不转义）
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 转换完成！结果已保存至: {output_path}")


if __name__ == "__main__":
    # 修改为你实际的文件路径（如果脚本和文件在同一目录）
    excel_file = "主题库数据.xlsx"
    excel_to_foreign_lang_json(excel_file)