def transfer(accountA, accountB, amount):
    if amount <= 0:
        raise ValueError("转账金额必须为正数")
    if accountA['balance'] < amount:
        raise ValueError("余额不足")
    accountA['balance'] -= amount
    accountB['balance'] += amount
    return True