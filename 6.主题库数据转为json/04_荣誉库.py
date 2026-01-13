import pandas as pd
import json

def excel_to_honor_json(excel_path, sheet_name="荣誉库", output_path="output/04_荣誉库.json"):
    """
    将 Excel 中 '荣誉库' sheet 转换为指定 JSON 格式。
    
    Args:
        excel_path (str): Excel 文件路径
        sheet_name (str): 工作表名称，默认为 "荣誉库"
        output_path (str): 输出 JSON 文件路径
    """
    # 读取 Excel 文件中的指定 sheet
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=0)

    # 清理列名：去除前后空格
    df.columns = df.columns.str.strip()

    # 检查必需列是否存在
    required_columns = ["荣誉名称", "荣誉级别", "授予单位"]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Excel 表 '{sheet_name}' 必须包含列: {required_columns}")

    # 填充 NaN 为 空字符串，便于后续处理
    df = df.fillna("")

    # 解析“荣誉级别”：按 '、' 拆分，若为空则返回空列表
    def parse_honor_level(level_str):
        if not level_str or level_str == "":
            return []
        return [part.strip() for part in str(level_str).split('、')]

    # 构建荣誉列表
    honor_list = []
    for _, row in df.iterrows():
        name = str(row["荣誉名称"]).strip()
        level_str = str(row["荣誉级别"]).strip()
        unit = str(row["授予单位"]).strip()

        # 如果荣誉名称为空，可选择跳过（根据需求）
        if not name:
            continue

        honor_list.append({
            "荣誉名称": name,
            "荣誉级别": parse_honor_level(level_str),
            "授予单位": unit if unit else ""
        })

    # 统计信息（可选）
    print(f"📊 数据统计:")
    print(f"   - 总荣誉条数: {len(honor_list)}")

    # 构造最终结果
    result = {"荣誉库列表": honor_list}

    # 写入 JSON 文件（UTF-8 编码，中文不转义）
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 转换完成！结果已保存至: {output_path}")


if __name__ == "__main__":
    # 修改为你实际的文件路径
    excel_file = "主题库数据.xlsx"
    excel_to_honor_json(excel_file)