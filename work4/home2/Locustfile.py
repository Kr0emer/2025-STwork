from locust import HttpUser, task, between
import random
import string

class UserBehavior(HttpUser):
    # 用户等待时间（模拟真实用户行为）
    wait_time = between(1, 3)
    
    def on_start(self):
        """每个用户启动时执行一次"""
        # 生成唯一的用户名和邮箱
        self.username = self.generate_random_username()
        self.email = f"{self.username}@test.com"
        self.password = "Test123456"
    
    def generate_random_username(self):
        """生成随机用户名"""
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"user_{random_str}"
    
    @task(3)
    def register(self):
        """注册任务（权重为 3）"""
        # 每次调用生成新的用户名和邮箱，避免冲突
        username = self.generate_random_username()
        email = f"{username}@test.com"
        
        with self.client.post(
            "/api/register",
            json={
                "username": username,
                "email": email,
                "password": self.password
            },
            catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
            elif response.status_code == 409:
                # 用户已存在，标记为成功（正常情况）
                response.success()
            else:
                response.failure(f"注册失败: {response.status_code}")
    
    @task(1)
    def login(self):
        """登录任务（权重为 1）"""
        with self.client.post(
            "/api/login",
            json={
                "username": self.username,
                "password": self.password
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                # 用户不存在，先注册
                self.register()
            else:
                response.failure(f"登录失败: {response.status_code}")
    
    @task(1)
    def health_check(self):
        """健康检查（权重为 1）"""
        with self.client.get("/api/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"健康检查失败: {response.status_code}")


# 高并发压力测试场景
class StressTestUser(HttpUser):
    """专门用于压力测试的用户类"""
    wait_time = between(0.5, 1.5)  # 更短的等待时间
    
    def on_start(self):
        self.counter = 0
    
    @task
    def concurrent_register(self):
        """高并发注册测试"""
        self.counter += 1
        username = f"stress_user_{self.counter}_{random.randint(1000, 9999)}"
        email = f"{username}@stress.com"
        
        with self.client.post(
            "/api/register",
            json={
                "username": username,
                "email": email,
                "password": "StressTest123"
            },
            catch_response=True
        ) as response:
            if response.status_code in [201, 409]:
                response.success()
            else:
                response.failure(f"状态码: {response.status_code}")