import pandas as pd
import json

def excel_to_major_json(excel_path, sheet_name="专业库", output_path="output/06_专业库.json"):
    # 读取Excel文件中的指定sheet
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=0)

    # 确保列名正确（可选：自动去除空格）
    df.columns = df.columns.str.strip()
    required_columns = ["门类", "专业类", "专业名称"]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Excel文件必须包含列: {required_columns}")

    # 去除空行（但保留原始顺序）
    df = df.dropna(subset=["门类", "专业类", "专业名称"]).reset_index(drop=True)

    # === 新增：统计原始数据条数 ===
    total_majors = len(df)
    total_menlei = df["门类"].nunique()
    total_zhuanye_lei = df["专业类"].nunique()

    print(f"📊 数据统计（去重前）:")
    print(f"   - 门类数量: {total_menlei}")
    print(f"   - 专业类数量: {total_zhuanye_lei}")
    print(f"   - 专业名称总条数: {total_majors}")

    # 构建嵌套结构（关键：groupby 设置 sort=False 以保持原始顺序）
    result = {"专业分类列表": []}
    grouped_by_menlei = df.groupby("门类", sort=False)  # 保持门类在Excel中的首次出现顺序

    for menlei, group1 in grouped_by_menlei:
        menlei_entry = {
            "门类名称": menlei,
            "专业类列表": []
        }
        grouped_by_zhuanye_lei = group1.groupby("专业类", sort=False)  # 保持专业类在该门类下的首次出现顺序
        for zhuanye_lei, group2 in grouped_by_zhuanye_lei:
            # 使用 unique() 保持专业名称在该专业类下的首次出现顺序
            zhuanye_names = group2["专业名称"].dropna().unique().tolist()
            menlei_entry["专业类列表"].append({
                "专业类名称": zhuanye_lei,
                "专业名称列表": zhuanye_names
            })
        result["专业分类列表"].append(menlei_entry)

    # 写入JSON文件（UTF-8编码，中文不转义）
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 转换完成！结果已保存至: {output_path}")


if __name__ == "__main__":
    # 修改为你实际的文件路径（如果脚本和文件在同一目录）
    excel_file = "主题库数据.xlsx"
    excel_to_major_json(excel_file)