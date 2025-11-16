def divide(a, b):
    return a / b  # 缺陷1: 未检查除数为0

def find_max(lst):
    max_val = 0  # 缺陷2: 如果列表全是负数，返回结果错误
    for x in lst:
        if x > max_val:
            max_val = x
    return max_val

def get_item(lst, idx):
    return lst[idx]  # 缺陷3: 未检查索引越界

get_item([1, 2, 3], 5)