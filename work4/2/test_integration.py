import requests
def test_order_api():
    url = "http://127.0.0.1:5000/order"
    res = requests.post(url, json={"item": "book", "qty": 2})
    assert res.status_code == 200
    assert res.json()["success"] == True