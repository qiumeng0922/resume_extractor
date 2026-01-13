import subprocess
import sys
import os

# 要执行的脚本列表（按顺序）
scripts = [
    "01_外语库.py",
    "02_计算机水平库.py",
    "03_职称库.py",
    "04_荣誉库.py",
    "05_院校库.py",
    "06_专业库.py"
]

def run_script(script_name):
    """运行单个 Python 脚本"""
    if not os.path.exists(script_name):
        print(f"⚠️ 脚本未找到: {script_name}")
        return False

    print(f"\n🚀 正在运行: {script_name}")
    print("=" * 50)
    
    try:
        # 使用当前 Python 解释器运行脚本
        result = subprocess.run([sys.executable, script_name], check=True)
        print(f"✅ 成功完成: {script_name}\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 运行失败: {script_name} (退出码: {e.returncode})\n")
        return False
    except Exception as e:
        print(f"💥 意外错误: {script_name} - {e}\n")
        return False

def main():
    print("🎯 一键启动所有数据转换脚本...\n")
    failed_scripts = []

    for script in scripts:
        success = run_script(script)
        if not success:
            failed_scripts.append(script)

    # 汇总结果
    print("\n" + "="*60)
    if failed_scripts:
        print(f"🚨 以下脚本运行失败，请检查:\n  - " + "\n  - ".join(failed_scripts))
    else:
        print("🎉 所有脚本已成功运行完毕！")

if __name__ == "__main__":
    main()