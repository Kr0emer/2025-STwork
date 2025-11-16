def isValidPassword(s: str) -> bool:
    # 类型检查
    if not isinstance(s, str):
        return False
    
    # 长度检查
    if len(s) < 6 or len(s) > 12:
        return False
    
    # 检查是否包含数字
    has_digit = any(char.isdigit() for char in s)
    
    # 检查是否包含字母
    has_letter = any(char.isalpha() for char in s)
    
    # 返回结果：必须同时包含数字和字母
    return has_digit and has_letter


# 测试代码
def run_tests():
    """运行所有测试用例"""
    
    # 等价类测试用例
    ec_test_cases = [
        ("Pass123", True, "有效密码（7位，含数字和字母）"),
        ("a1b2c3", True, "有效密码（6位最小长度）"),
        ("ABCdef123456", True, "有效密码（12位最大长度）"),
        ("a1@#$", False, "长度不足（5位）"),
        ("a1b2c3d4e5f6g7", False, "长度超出（14位）"),
        ("abcdef", False, "只有字母，无数字"),
        ("123456", False, "只有数字，无字母"),
        ("@#$%^&", False, "只有特殊字符"),
        ("", False, "空字符串"),
        (None, False, "空值输入"),
        (123456, False, "非字符串类型（整数）"),
    ]
    
    # 边界值测试用例
    bv_test_cases = [
        ("a1b2c", False, "下边界外（5位）"),
        ("a1b2c3", True, "下边界值（6位）"),
        ("a1b2c3d", True, "下边界内（7位）"),
        ("a1b2c3d4e5f", True, "上边界内（11位）"),
        ("a1b2c3d4e5f6", True, "上边界值（12位）"),
        ("a1b2c3d4e5f6g", False, "上边界外（13位）"),
        ("aaaaa1", True, "最少数字边界"),
        ("11111a", True, "最少字母边界"),
        ("1aaaaa", True, "数字在首位"),
        ("aaaaa1", True, "数字在末位"),
        ("aaa1aa", True, "数字在中间"),
    ]
    
    # 特殊场景测试
    special_test_cases = [
        ("Aa1!@#", True, "包含大小写字母、数字、特殊字符"),
        (" abc123", True, "包含空格（首位）"),
        ("abc 123", True, "包含空格（中间）"),
        ("ABC123", True, "全大写字母+数字"),
        ("abc123", True, "全小写字母+数字"),
    ]
    
    # 执行测试
    print("="*60)
    print("密码验证函数测试报告")
    print("="*60)
    
    all_tests = [
        ("等价类划分测试", ec_test_cases),
        ("边界值分析测试", bv_test_cases),
        ("特殊场景测试", special_test_cases)
    ]
    
    total_passed = 0
    total_failed = 0
    
    for test_type, test_cases in all_tests:
        print(f"\n【{test_type}】")
        print("-"*50)
        
        for test_input, expected, description in test_cases:
            try:
                actual = isValidPassword(test_input)
                status = "✓ PASS" if actual == expected else "✗ FAIL"
                
                if actual == expected:
                    total_passed += 1
                else:
                    total_failed += 1
                
                # 格式化输入显示
                if test_input is None:
                    input_display = "None"
                elif isinstance(test_input, str):
                    input_display = f'"{test_input}"'
                else:
                    input_display = str(test_input)
                
                print(f"{status} | 输入: {input_display:<20} | 期望: {expected:<5} | 实际: {actual:<5} | {description}")
                
            except Exception as e:
                print(f"✗ ERROR | 输入: {test_input} | 错误: {e}")
                total_failed += 1
    
    # 测试总结
    print("\n" + "="*60)
    print("测试总结")
    print("-"*50)
    print(f"总测试用例数: {total_passed + total_failed}")
    print(f"通过: {total_passed}")
    print(f"失败: {total_failed}")
    print(f"通过率: {total_passed/(total_passed + total_failed)*100:.2f}%")
    print("="*60)


# 运行测试
if __name__ == "__main__":
    run_tests()
    
    # 交互式测试
    print("\n【交互式测试】")
    print("输入 'quit' 退出")
    while True:
        password = input("\n请输入要测试的密码: ")
        if password.lower() == 'quit':
            break
        result = isValidPassword(password)
        print(f"验证结果: {'有效密码 ✓' if result else '无效密码 ✗'}")
        
        if not result:
            # 提供失败原因分析
            if not isinstance(password, str):
                print("原因: 输入不是字符串类型")
            elif len(password) < 6:
                print(f"原因: 长度不足（当前{len(password)}位，需要至少6位）")
            elif len(password) > 12:
                print(f"原因: 长度超出（当前{len(password)}位，最多12位）")
            elif not any(c.isdigit() for c in password):
                print("原因: 不包含数字")
            elif not any(c.isalpha() for c in password):
                print("原因: 不包含字母")