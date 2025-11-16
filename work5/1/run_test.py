#!/usr/bin/env python3
"""
测试执行脚本
快速运行测试并生成报告
"""
import os
import sys
import subprocess
from datetime import datetime

def print_header(text):
    """打印标题"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def run_command(cmd, description):
    """运行命令"""
    print(f">>> {description}")
    print(f">>> 执行命令: {cmd}\n")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def main():
    """主函数"""
    print_header("Web登录功能自动化测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建报告目录
    os.makedirs('reports', exist_ok=True)
    
    # 检查依赖
    print_header("1. 检查环境")
    if not run_command("pip list | grep pytest", "检查pytest是否安装"):
        print("❌ pytest未安装，正在安装依赖...")
        run_command("pip install -r requirements.txt", "安装依赖包")
    else:
        print("✅ pytest已安装")
    
    # 运行测试
    print_header("2. 运行测试用例")
    test_cmd = (
        "pytest test_app.py -v "
        "--html=reports/test_report.html "
        "--self-contained-html "
        "--cov=app "
        "--cov-report=html:reports/coverage "
        "--cov-report=term"
    )
    
    success = run_command(test_cmd, "执行自动化测试")
    
    # 测试结果
    print_header("3. 测试结果")
    if success:
        print("✅ 所有测试通过!")
    else:
        print("❌ 部分测试失败，请查看报告")
    
    # 生成报告位置
    print_header("4. 测试报告")
    print("📊 HTML测试报告: reports/test_report.html")
    print("📈 覆盖率报告: reports/coverage/index.html")
    
    print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*60)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())