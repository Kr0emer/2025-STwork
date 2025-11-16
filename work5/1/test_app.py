"""
Web登录功能自动化测试
使用pytest框架进行测试
"""
import pytest
from app import app, USERS

@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as client:
        yield client

@pytest.fixture
def logged_in_client(client):
    """创建已登录的测试客户端"""
    client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    yield client

class TestLoginPage:
    """测试登录页面"""
    
    def test_login_page_loads(self, client):
        """测试用例1: 登录页面能否正常加载"""
        response = client.get('/login')
        assert response.status_code == 200
        assert '用户登录'.encode('utf-8') in response.data
        assert '用户名'.encode('utf-8') in response.data
        assert '密码'.encode('utf-8') in response.data
    
    def test_index_redirects_to_login(self, client):
        """测试用例2: 未登录访问首页应重定向到登录页"""
        response = client.get('/', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location

class TestLoginFunctionality:
    """测试登录功能"""
    
    def test_valid_login(self, client):
        """测试用例3: 有效用户名和密码登录成功"""
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert '欢迎来到用户中心'.encode('utf-8') in response.data
        assert 'admin'.encode('utf-8') in response.data
    
    def test_invalid_username(self, client):
        """测试用例4: 无效用户名登录失败"""
        response = client.post('/login', data={
            'username': 'invalid_user',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert '用户名或密码错误'.encode('utf-8') in response.data
    
    def test_invalid_password(self, client):
        """测试用例5: 错误密码登录失败"""
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert '用户名或密码错误'.encode('utf-8') in response.data
    
    def test_empty_username(self, client):
        """测试用例6: 空用户名登录失败"""
        response = client.post('/login', data={
            'username': '',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert '用户名不能为空'.encode('utf-8') in response.data
    
    def test_empty_password(self, client):
        """测试用例7: 空密码登录失败"""
        response = client.post('/login', data={
            'username': 'admin',
            'password': ''
        }, follow_redirects=True)
        assert response.status_code == 200
        assert '密码不能为空'.encode('utf-8') in response.data
    
    def test_whitespace_username(self, client):
        """测试用例8: 用户名带空格应被处理"""
        response = client.post('/login', data={
            'username': '  admin  ',
            'password': 'admin123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert '欢迎来到用户中心'.encode('utf-8') in response.data
    
    def test_multiple_users_login(self, client):
        """测试用例9: 测试多个用户登录"""
        # 测试user1
        response = client.post('/login', data={
            'username': 'user1',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert 'user1'.encode('utf-8') in response.data
        
        # 退出
        client.get('/logout')
        
        # 测试test用户
        response = client.post('/login', data={
            'username': 'test',
            'password': 'test123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert 'test'.encode('utf-8') in response.data

class TestDashboard:
    """测试用户中心页面"""
    
    def test_dashboard_requires_login(self, client):
        """测试用例10: 未登录访问用户中心应重定向到登录页"""
        response = client.get('/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_dashboard_with_login(self, logged_in_client):
        """测试用例11: 已登录用户可以访问用户中心"""
        response = logged_in_client.get('/dashboard')
        assert response.status_code == 200
        assert '欢迎来到用户中心'.encode('utf-8') in response.data
        assert 'admin'.encode('utf-8') in response.data

class TestLogout:
    """测试退出登录功能"""
    
    def test_logout(self, logged_in_client):
        """测试用例12: 退出登录功能"""
        # 确认已登录
        response = logged_in_client.get('/dashboard')
        assert response.status_code == 200
        
        # 退出登录
        response = logged_in_client.get('/logout', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
        
        # 确认已退出，无法访问dashboard
        response = logged_in_client.get('/dashboard', follow_redirects=False)
        assert response.status_code == 302

class TestAPILogin:
    """测试API登录接口"""
    
    def test_api_login_success(self, client):
        """测试用例13: API登录成功"""
        response = client.post('/api/login',
                              json={'username': 'admin', 'password': 'admin123'})
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        assert json_data['message'] == '登录成功'
        assert json_data['username'] == 'admin'
    
    def test_api_login_failure(self, client):
        """测试用例14: API登录失败"""
        response = client.post('/api/login',
                              json={'username': 'admin', 'password': 'wrongpass'})
        assert response.status_code == 401
        json_data = response.get_json()
        assert json_data['success'] is False
        assert '用户名或密码错误' in json_data['message']
    
    def test_api_login_empty_credentials(self, client):
        """测试用例15: API登录空凭证"""
        response = client.post('/api/login',
                              json={'username': '', 'password': ''})
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data['success'] is False

class TestSecurity:
    """测试安全性"""
    
    def test_session_management(self, client):
        """测试用例16: Session管理"""
        # 登录
        with client.session_transaction() as sess:
            assert 'username' not in sess
        
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        with client.session_transaction() as sess:
            assert 'username' in sess
            assert sess['username'] == 'admin'
    
    def test_sql_injection_attempt(self, client):
        """测试用例17: SQL注入尝试（应该失败）"""
        response = client.post('/login', data={
            'username': "admin' OR '1'='1",
            'password': "anything"
        }, follow_redirects=True)
        assert response.status_code == 200
        assert '用户名或密码错误'.encode('utf-8') in response.data

class TestEdgeCases:
    """测试边界情况"""
    
    def test_very_long_username(self, client):
        """测试用例18: 超长用户名"""
        long_username = 'a' * 1000
        response = client.post('/login', data={
            'username': long_username,
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert '用户名或密码错误'.encode('utf-8') in response.data
    
    def test_special_characters_in_username(self, client):
        """测试用例19: 用户名包含特殊字符"""
        response = client.post('/login', data={
            'username': '<script>alert("xss")</script>',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert '用户名或密码错误'.encode('utf-8') in response.data
    
    def test_unicode_characters(self, client):
        """测试用例20: Unicode字符"""
        response = client.post('/login', data={
            'username': '管理员',
            'password': '密码123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert '用户名或密码错误'.encode('utf-8') in response.data