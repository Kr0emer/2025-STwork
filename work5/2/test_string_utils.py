"""
字符串处理工具模块的单元测试
使用pytest框架进行测试
"""
import pytest
from string_utils import (
    is_palindrome,
    reverse_string,
    count_vowels,
    remove_duplicates,
    capitalize_words
)


class TestIsPalindrome:
    """测试回文判断函数"""
    
    def test_simple_palindrome(self):
        """测试简单的回文字符串"""
        assert is_palindrome("madam") is True
        assert is_palindrome("racecar") is True
        assert is_palindrome("level") is True
    
    def test_not_palindrome(self):
        """测试非回文字符串"""
        assert is_palindrome("hello") is False
        assert is_palindrome("python") is False
        assert is_palindrome("world") is False
    
    def test_single_character(self):
        """测试单字符字符串"""
        assert is_palindrome("a") is True
        assert is_palindrome("Z") is True
    
    def test_empty_string(self):
        """测试空字符串"""
        assert is_palindrome("") is True
    
    def test_palindrome_with_spaces(self):
        """测试包含空格的回文"""
        assert is_palindrome("A man a plan a canal Panama") is True
        assert is_palindrome("race a car") is False
    
    def test_case_insensitive(self):
        """测试大小写不敏感"""
        assert is_palindrome("Madam") is True
        assert is_palindrome("RaceCar") is True
        assert is_palindrome("AbA") is True
    
    def test_numeric_palindrome(self):
        """测试包含数字的回文"""
        assert is_palindrome("12321") is True
        assert is_palindrome("12345") is False
    
    def test_invalid_type(self):
        """测试无效输入类型"""
        with pytest.raises(TypeError):
            is_palindrome(123)
        with pytest.raises(TypeError):
            is_palindrome(None)
        with pytest.raises(TypeError):
            is_palindrome([1, 2, 3])


class TestReverseString:
    """测试字符串反转函数"""
    
    def test_normal_string(self):
        """测试普通字符串反转"""
        assert reverse_string("hello") == "olleh"
        assert reverse_string("python") == "nohtyp"
    
    def test_single_character(self):
        """测试单字符反转"""
        assert reverse_string("a") == "a"
    
    def test_empty_string(self):
        """测试空字符串反转"""
        assert reverse_string("") == ""
    
    def test_string_with_spaces(self):
        """测试包含空格的字符串反转"""
        assert reverse_string("hello world") == "dlrow olleh"
    
    def test_palindrome_reverse(self):
        """测试回文反转"""
        assert reverse_string("madam") == "madam"
    
    def test_invalid_type(self):
        """测试无效输入类型"""
        with pytest.raises(TypeError):
            reverse_string(123)


class TestCountVowels:
    """测试元音统计函数"""
    
    def test_string_with_vowels(self):
        """测试包含元音的字符串"""
        assert count_vowels("hello") == 2
        assert count_vowels("programming") == 3
        assert count_vowels("aeiou") == 5
    
    def test_string_without_vowels(self):
        """测试不包含元音的字符串"""
        assert count_vowels("bcdfg") == 0
        assert count_vowels("xyz") == 0
    
    def test_empty_string(self):
        """测试空字符串"""
        assert count_vowels("") == 0
    
    def test_uppercase_vowels(self):
        """测试大写元音"""
        assert count_vowels("HELLO") == 2
        assert count_vowels("AEIOU") == 5
    
    def test_mixed_case(self):
        """测试大小写混合"""
        assert count_vowels("HeLLo WoRLd") == 3
    
    def test_with_numbers(self):
        """测试包含数字的字符串"""
        assert count_vowels("hello123") == 2
    
    def test_invalid_type(self):
        """测试无效输入类型"""
        with pytest.raises(TypeError):
            count_vowels(123)


class TestRemoveDuplicates:
    """测试移除重复字符函数"""
    
    def test_string_with_duplicates(self):
        """测试包含重复字符的字符串"""
        assert remove_duplicates("hello") == "helo"
        assert remove_duplicates("programming") == "progamin"
    
    def test_string_without_duplicates(self):
        """测试不包含重复字符的字符串"""
        assert remove_duplicates("abcdef") == "abcdef"
    
    def test_all_duplicates(self):
        """测试全是重复字符"""
        assert remove_duplicates("aaaa") == "a"
        assert remove_duplicates("1111") == "1"
    
    def test_empty_string(self):
        """测试空字符串"""
        assert remove_duplicates("") == ""
    
    def test_single_character(self):
        """测试单字符"""
        assert remove_duplicates("a") == "a"
    
    def test_preserve_order(self):
        """测试保持首次出现顺序"""
        assert remove_duplicates("abcabc") == "abc"
    
    def test_invalid_type(self):
        """测试无效输入类型"""
        with pytest.raises(TypeError):
            remove_duplicates(123)


class TestCapitalizeWords:
    """测试单词首字母大写函数"""
    
    def test_lowercase_words(self):
        """测试小写单词"""
        assert capitalize_words("hello world") == "Hello World"
        assert capitalize_words("python programming") == "Python Programming"
    
    def test_already_capitalized(self):
        """测试已大写的单词"""
        assert capitalize_words("Hello World") == "Hello World"
    
    def test_mixed_case(self):
        """测试大小写混合"""
        assert capitalize_words("hELLo WoRLd") == "Hello World"
    
    def test_single_word(self):
        """测试单个单词"""
        assert capitalize_words("hello") == "Hello"
    
    def test_empty_string(self):
        """测试空字符串"""
        assert capitalize_words("") == ""
    
    def test_multiple_spaces(self):
        """测试多个空格"""
        # split()会合并多个空格，这是Python的标准行为
        assert capitalize_words("hello  world") == "Hello World"
    
    def test_invalid_type(self):
        """测试无效输入类型"""
        with pytest.raises(TypeError):
            capitalize_words(123)


class TestEdgeCases:
    """测试边界情况"""
    
    def test_special_characters(self):
        """测试特殊字符"""
        assert is_palindrome("a!b!a") is True
        assert count_vowels("!@#$%") == 0
        assert remove_duplicates("!!@@") == "!@"
    
    def test_unicode_characters(self):
        """测试Unicode字符"""
        assert reverse_string("你好") == "好你"
        assert remove_duplicates("中中国国") == "中国"
    
    def test_very_long_string(self):
        """测试超长字符串"""
        long_string = "a" * 10000
        assert is_palindrome(long_string) is True
        assert len(remove_duplicates(long_string)) == 1


# 参数化测试示例
@pytest.mark.parametrize("input_str,expected", [
    ("madam", True),
    ("racecar", True),
    ("hello", False),
    ("A", True),
    ("", True),
])
def test_palindrome_parametrized(input_str, expected):
    """参数化测试回文判断"""
    assert is_palindrome(input_str) == expected


@pytest.mark.parametrize("input_str,expected", [
    ("hello", 2),
    ("aeiou", 5),
    ("xyz", 0),
    ("HELLO", 2),
    ("", 0),
])
def test_count_vowels_parametrized(input_str, expected):
    """参数化测试元音统计"""
    assert count_vowels(input_str) == expected