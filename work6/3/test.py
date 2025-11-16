"""
自动化测试套件 - 无需手动启动服务
使用 multiprocessing 在测试前自动启动服务，测试后自动关闭

运行方式: pytest test_checkout_auto.py -v
"""

import pytest
import requests
import time
import multiprocessing
from contextlib import contextmanager


# 测试配置
BASE_URL = "http://127.0.0.1:5000"
CHECKOUT_URL = f"{BASE_URL}/checkout"
HEALTH_URL = f"{BASE_URL}/health"


def run_server():
    """
    在子进程中运行 Flask 服务器
    """
    # 延迟导入，避免在主进程中加载 Flask
    import sys
    import os
    
    # 添加当前目录到 Python 路径
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from app import app
    
    # 禁用 Flask 的调试输出
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    # 运行服务器
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


@contextmanager
def flask_server():
    """
    上下文管理器：自动启动和停止 Flask 服务器
    
    用法:
        with flask_server():
            # 在这里运行测试
            response = requests.get("http://127.0.0.1:5000/health")
    """
    # 启动服务器进程
    process = multiprocessing.Process(target=run_server)
    process.start()
    
    # 等待服务器启动
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(HEALTH_URL, timeout=1)
            if response.status_code == 200:
                print(f"\n✅ 服务器已启动 (耗时 {i+1} 秒)")
                break
        except requests.exceptions.RequestException:
            time.sleep(1)
    else:
        process.terminate()
        process.join(timeout=5)
        raise RuntimeError("服务器启动失败")
    
    try:
        yield process
    finally:
        # 清理：终止服务器进程
        process.terminate()
        process.join(timeout=5)
        if process.is_alive():
            process.kill()
            process.join()
        print("\n🛑 服务器已关闭")


@pytest.fixture(scope="session")
def server():
    """
    Pytest fixture: 在整个测试会话期间启动一次服务器
    """
    with flask_server() as proc:
        yield proc


class TestCheckoutAutomatic:
    """自动化测试类 - 使用 session-scoped fixture"""
    
    def test_server_health(self, server):
        """测试服务器健康状态"""
        response = requests.get(HEALTH_URL)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_checkout_total(self, server):
        """测试结账总价计算 - 原始示例"""
        data = {"items": [{"price": 20, "quantity": 3}]}
        res = requests.post(CHECKOUT_URL, json=data)
        assert res.status_code == 200
        assert res.json()["total"] == 60
    
    def test_single_item(self, server):
        """测试单商品结账"""
        data = {"items": [{"price": 100, "quantity": 1}]}
        res = requests.post(CHECKOUT_URL, json=data)
        assert res.status_code == 200
        assert res.json()["total"] == 100
    
    def test_multiple_items(self, server):
        """测试多商品结账"""
        data = {
            "items": [
                {"price": 100, "quantity": 2},
                {"price": 50, "quantity": 3}
            ]
        }
        res = requests.post(CHECKOUT_URL, json=data)
        assert res.status_code == 200
        assert res.json()["total"] == 350
    
    def test_empty_cart(self, server):
        """测试空购物车"""
        data = {"items": []}
        res = requests.post(CHECKOUT_URL, json=data)
        assert res.status_code == 400
        assert "error" in res.json()
        assert res.json()["error"] == "empty cart"
    
    def test_decimal_prices(self, server):
        """测试小数价格"""
        data = {"items": [{"price": 19.99, "quantity": 3}]}
        res = requests.post(CHECKOUT_URL, json=data)
        assert res.status_code == 200
        assert abs(res.json()["total"] - 59.97) < 0.01


class TestCheckoutPerTest:
    """每个测试都启动/关闭服务器（用于演示，实际不推荐）"""
    
    def test_with_individual_server(self):
        """
        每个测试独立启动服务器
        注意：这种方式较慢，仅用于演示
        """
        # 启动服务器
        p = multiprocessing.Process(target=run_server)
        p.start()
        time.sleep(2)  # 等待服务器启动
        
        try:
            # 执行测试
            data = {"items": [{"price": 20, "quantity": 3}]}
            res = requests.post(CHECKOUT_URL, json=data)
            assert res.status_code == 200
            assert res.json()["total"] == 60
        finally:
            # 清理
            p.terminate()
            p.join(timeout=5)
            if p.is_alive():
                p.kill()


class TestIntegration:
    """集成测试 - 测试完整的工作流程"""
    
    def test_complete_checkout_workflow(self, server):
        """测试完整的结账工作流程"""
        # 1. 健康检查
        health_res = requests.get(HEALTH_URL)
        assert health_res.status_code == 200
        
        # 2. 正常结账
        checkout_data = {
            "items": [
                {"price": 99.99, "quantity": 1},
                {"price": 49.99, "quantity": 2}
            ]
        }
        checkout_res = requests.post(CHECKOUT_URL, json=checkout_data)
        assert checkout_res.status_code == 200
        assert abs(checkout_res.json()["total"] - 199.97) < 0.01
        
        # 3. 尝试空购物车
        empty_res = requests.post(CHECKOUT_URL, json={"items": []})
        assert empty_res.status_code == 400
        
        # 4. 再次健康检查
        health_res2 = requests.get(HEALTH_URL)
        assert health_res2.status_code == 200


def test_standalone_example():
    """
    独立测试示例 - 不依赖 fixture
    完全按照你提供的模式实现
    """
    # 启动服务器
    p = multiprocessing.Process(target=run_server)
    p.start()
    time.sleep(2)
    
    try:
        # 测试
        data = {"items": [{"price": 20, "quantity": 3}]}
        res = requests.post(CHECKOUT_URL, json=data)
        assert res.status_code == 200
        assert res.json()["total"] == 60
        print("✅ 独立测试通过")
    finally:
        # 清理
        p.terminate()
        p.join(timeout=5)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])