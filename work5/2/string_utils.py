"""
字符串处理工具模块
包含回文判断、字符串反转等常用函数
"""


def is_palindrome(text):
    """
    判断字符串是否为回文

    Args:
        text (str): 待检查的字符串

    Returns:
        bool: 如果是回文返回True，否则返回False

    Examples:
        >>> is_palindrome("madam")
        True
        >>> is_palindrome("hello")
        False
    """
    if not isinstance(text, str):
        raise TypeError("输入必须是字符串类型")

    if not text:
        return True

    # 转换为小写并移除空格
    cleaned_text = text.lower().replace(" ", "")

    # 比较字符串与其反转
    return cleaned_text == cleaned_text[::-1]


def reverse_string(text):
    """
    反转字符串

    Args:
        text (str): 待反转的字符串

    Returns:
        str: 反转后的字符串

    Examples:
        >>> reverse_string("hello")
        'olleh'
    """
    if not isinstance(text, str):
        raise TypeError("输入必须是字符串类型")

    return text[::-1]


def count_vowels(text):
    """
    统计字符串中元音字母的数量

    Args:
        text (str): 待统计的字符串

    Returns:
        int: 元音字母的数量

    Examples:
        >>> count_vowels("hello")
        2
        >>> count_vowels("programming")
        3
    """
    if not isinstance(text, str):
        raise TypeError("输入必须是字符串类型")

    vowels = "aeiouAEIOU"
    return sum(1 for char in text if char in vowels)


def remove_duplicates(text):
    """
    移除字符串中的重复字符（保留首次出现）

    Args:
        text (str): 待处理的字符串

    Returns:
        str: 移除重复字符后的字符串

    Examples:
        >>> remove_duplicates("hello")
        'helo'
        >>> remove_duplicates("programming")
        'progamin'
    """
    if not isinstance(text, str):
        raise TypeError("输入必须是字符串类型")

    seen = set()
    result = []

    for char in text:
        if char not in seen:
            seen.add(char)
            result.append(char)

    return ''.join(result)


def capitalize_words(text):
    """
    将字符串中每个单词的首字母大写

    Args:
        text (str): 待处理的字符串

    Returns:
        str: 首字母大写后的字符串

    Examples:
        >>> capitalize_words("hello world")
        'Hello World'
    """
    if not isinstance(text, str):
        raise TypeError("输入必须是字符串类型")

    return ' '.join(word.capitalize() for word in text.split())