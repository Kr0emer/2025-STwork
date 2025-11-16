#!/usr/bin/env python3
"""
单元测试自动化运行脚本
自动执行pytest测试、生成覆盖率报告、运行pylint检查
"""
import subprocess
import sys
import os
from datetime import datetime


def print_section(title, char="="):
    """打印分节标题"""
    print(f"\n{char * 70}")
    print(f"  {title}")
    print(f"{char * 70}\n")


def run_command(cmd, description):
    """运行命令并返回结果"""
    print(f">>> {description}")
    print(f">>> 执行命令: {cmd}\n")
    result = subprocess.run(cmd, shell=True, capture_output=False)
    return result.returncode == 0


def main():
    """主函数"""
    print_section("Python单元测试自动化执行", "=")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 检查依赖
    print_section("1. 检查环境依赖", "-")
    if not run_command("pip list | grep pytest", "检查pytest"):
        print("正在安装依赖...")
        run_command("pip install -r requirements.txt --break-system-packages", 
                   "安装所需包")
    
    # 运行pytest测试
    print_section("2. 运行Pytest单元测试", "-")
    test_cmd = (
        "pytest test_string_utils.py -v "
        "--cov=string_utils "
        "--cov-report=html:htmlcov "
        "--cov-report=term-missing "
        "--html=test_report.html "
        "--self-contained-html"
    )
    test_success = run_command(test_cmd, "执行单元测试")
    
    # 生成覆盖率报告
    print_section("3. 生成详细覆盖率报告", "-")
    run_command("coverage report -m", "显示覆盖率详情")
    
    # 运行pylint检查
    print_section("4. 运行Pylint代码质量检查", "-")
    pylint_cmd = "pylint string_utils.py --rcfile=.pylintrc"
    run_command(pylint_cmd, "检查代码质量")
    
    # 生成评分报告
    print_section("5. Pylint评分详情", "-")
    run_command(f"{pylint_cmd} --score=yes", "获取Pylint评分")
    
    # 测试结果总结
    print_section("6. 测试结果总结", "=")
    
    if test_success:
        print("✅ 单元测试: 全部通过")
    else:
        print("❌ 单元测试: 存在失败")
    
    print("\n📊 生成的报告文件:")
    print("  - HTML测试报告: test_report.html")
    print("  - 覆盖率报告: htmlcov/index.html")
    print("  - Coverage详情: 终端已显示")
    print("  - Pylint评分: 终端已显示")
    
    print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return 0 if test_success else 1


if __name__ == '__main__':
    sys.exit(main())