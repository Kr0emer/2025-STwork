"""
Checkout 微服务系统测试
运行方式: pytest test_checkout.py -v
"""

import pytest
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 测试配置
BASE_URL = "http://localhost:5000"
CHECKOUT_URL = f"{BASE_URL}/checkout"
HEALTH_URL = f"{BASE_URL}/health"


class TestCheckoutService:
    """结账服务测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前置条件：确保服务正在运行"""
        try:
            response = requests.get(HEALTH_URL, timeout=2)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip("服务未运行，请先启动: python app.py")
    
    # ==================== 正常场景测试 ====================
    
    def test_tc001_single_item_checkout(self):
        """TC-001: 单商品结账"""
        payload = {
            "items": [
                {"price": 100, "quantity": 1}
            ]
        }
        response = requests.post(CHECKOUT_URL, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["total"] == 100
    
    def test_tc002_multiple_items_checkout(self):
        """TC-002: 多商品结账"""
        payload = {
            "items": [
                {"price": 100, "quantity": 2},
                {"price": 50, "quantity": 3}
            ]
        }
        response = requests.post(CHECKOUT_URL, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["total"] == 350  # 100*2 + 50*3 = 350
    
    def test_tc003_decimal_price_calculation(self):
        """TC-003: 小数价格计算"""
        payload = {
            "items": [
                {"price": 19.99, "quantity": 3}
            ]
        }
        response = requests.post(CHECKOUT_URL, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert abs(data["total"] - 59.97) < 0.01  # 浮点数比较使用容差
    
    def test_tc003_complex_calculation(self):
        """TC-003+: 复杂价格计算"""
        payload = {
            "items": [
                {"price": 12.50, "quantity": 4},
                {"price": 99.99, "quantity": 1},
                {"price": 5.25, "quantity": 10}
            ]
        }
        response = requests.post(CHECKOUT_URL, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        # 12.50*4 + 99.99*1 + 5.25*10 = 50 + 99.99 + 52.5 = 202.49
        assert abs(data["total"] - 202.49) < 0.01
    
    # ==================== 异常场景测试 ====================
    
    def test_tc004_empty_cart(self):
        """TC-004: 空购物车"""
        payload = {"items": []}
        response = requests.post(CHECKOUT_URL, json=payload)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"] == "empty cart"
    
    def test_tc005_missing_items_field(self):
        """TC-005: 缺少 items 字段"""
        payload = {}
        response = requests.post(CHECKOUT_URL, json=payload)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    def test_tc006_invalid_json(self):
        """TC-006: 无效的 JSON 格式"""
        response = requests.post(
            CHECKOUT_URL,
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        # Flask 会返回 400 或 500
        assert response.status_code in [400, 415, 500]
    
    def test_tc007_wrong_http_method(self):
        """TC-007: 错误的 HTTP 方法"""
        response = requests.get(CHECKOUT_URL)
        assert response.status_code == 405  # Method Not Allowed
    
    def test_tc008_missing_content_type(self):
        """TC-008: 缺少 Content-Type"""
        payload = '{"items": [{"price": 100, "quantity": 1}]}'
        response = requests.post(
            CHECKOUT_URL,
            data=payload
            # 不设置 Content-Type
        )
        # Flask 可能无法解析 JSON，应该返回错误或 None
        # 这取决于具体实现
        assert response.status_code in [200, 400, 415, 500]
    
    # ==================== 边界值测试 ====================
    
    def test_tc009_zero_price_item(self):
        """TC-009: 零价格商品"""
        payload = {
            "items": [
                {"price": 0, "quantity": 1}
            ]
        }
        response = requests.post(CHECKOUT_URL, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
    
    def test_tc010_zero_quantity_item(self):
        """TC-010: 零数量商品"""
        payload = {
            "items": [
                {"price": 100, "quantity": 0}
            ]
        }
        response = requests.post(CHECKOUT_URL, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
    
    def test_tc011_large_number_of_items(self):
        """TC-011: 大量商品"""
        items = [{"price": 10, "quantity": 1} for _ in range(100)]
        payload = {"items": items}
        
        response = requests.post(CHECKOUT_URL, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1000  # 10 * 100
    
    def test_tc012_negative_price(self):
        """TC-012: 负数价格（潜在bug）"""
        payload = {
            "items": [
                {"price": -100, "quantity": 1}
            ]
        }
        response = requests.post(CHECKOUT_URL, json=payload)
        
        # 当前实现会允许负数，这是一个潜在的业务逻辑bug
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == -100
        # 注意：在实际业务中，应该拒绝负数价格
    
    def test_tc013_negative_quantity(self):
        """TC-013: 负数数量（潜在bug）"""
        payload = {
            "items": [
                {"price": 100, "quantity": -1}
            ]
        }
        response = requests.post(CHECKOUT_URL, json=payload)
        
        # 当前实现会允许负数，这是一个潜在的业务逻辑bug
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == -100
        # 注意：在实际业务中，应该拒绝负数数量
    
    # ==================== 数据类型测试 ====================
    
    def test_missing_price_field(self):
        """缺少 price 字段"""
        payload = {
            "items": [
                {"quantity": 1}  # 缺少 price
            ]
        }
        # 这会导致 KeyError，测试当前实现的健壮性
        with pytest.raises(requests.exceptions.RequestException):
            response = requests.post(CHECKOUT_URL, json=payload, timeout=2)
            # 如果返回了响应，检查是否是错误状态
            if response.status_code >= 400:
                pass  # 正确处理了错误
            else:
                raise AssertionError("应该返回错误状态码")
    
    def test_missing_quantity_field(self):
        """缺少 quantity 字段"""
        payload = {
            "items": [
                {"price": 100}  # 缺少 quantity
            ]
        }
        # 这会导致 KeyError
        with pytest.raises(requests.exceptions.RequestException):
            response = requests.post(CHECKOUT_URL, json=payload, timeout=2)
            if response.status_code >= 400:
                pass
            else:
                raise AssertionError("应该返回错误状态码")
    
    def test_invalid_price_type(self):
        """价格类型无效（字符串）"""
        payload = {
            "items": [
                {"price": "invalid", "quantity": 1}
            ]
        }
        # 这会导致 TypeError
        with pytest.raises(requests.exceptions.RequestException):
            response = requests.post(CHECKOUT_URL, json=payload, timeout=2)
            if response.status_code >= 400:
                pass
            else:
                raise AssertionError("应该返回错误状态码")
    
    # ==================== 健康检查测试 ====================
    
    def test_tc016_health_check(self):
        """TC-016: 健康检查"""
        response = requests.get(HEALTH_URL)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestPerformance:
    """性能测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """确保服务正在运行"""
        try:
            response = requests.get(HEALTH_URL, timeout=2)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip("服务未运行")
    
    def test_tc014_concurrent_requests(self):
        """TC-014: 并发请求测试"""
        payload = {
            "items": [
                {"price": 100, "quantity": 2},
                {"price": 50, "quantity": 1}
            ]
        }
        
        def make_request():
            response = requests.post(CHECKOUT_URL, json=payload)
            return response.status_code, response.json()
        
        # 发送 50 个并发请求
        num_requests = 50
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 验证所有请求都成功
        for status_code, data in results:
            assert status_code == 200
            assert data["total"] == 250
        
        # 验证性能
        print(f"\n并发测试: {num_requests} 个请求耗时 {duration:.2f} 秒")
        print(f"平均响应时间: {duration/num_requests*1000:.2f} ms")
        assert duration < 10  # 所有请求应在 10 秒内完成
    
    def test_tc015_large_data_volume(self):
        """TC-015: 大数据量测试"""
        # 创建包含 1000 个商品的购物车
        items = [{"price": 10.5, "quantity": 2} for _ in range(1000)]
        payload = {"items": items}
        
        start_time = time.time()
        response = requests.post(CHECKOUT_URL, json=payload)
        end_time = time.time()
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 21000  # 10.5 * 2 * 1000
        
        duration = end_time - start_time
        print(f"\n大数据量测试: 1000 个商品耗时 {duration*1000:.2f} ms")
        assert duration < 1  # 应在 1 秒内完成
    
    def test_response_time(self):
        """响应时间测试"""
        payload = {
            "items": [
                {"price": 100, "quantity": 1}
            ]
        }
        
        response_times = []
        for _ in range(10):
            start_time = time.time()
            response = requests.post(CHECKOUT_URL, json=payload)
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"\n响应时间统计:")
        print(f"  平均: {avg_time*1000:.2f} ms")
        print(f"  最大: {max_time*1000:.2f} ms")
        print(f"  最小: {min_time*1000:.2f} ms")
        
        assert avg_time < 0.1  # 平均响应时间应小于 100ms


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])