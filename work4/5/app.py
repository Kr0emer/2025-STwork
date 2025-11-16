"""
⚠️ 警告：此代码故意包含 SQL 注入漏洞，仅用于教育和测试目的
切勿在生产环境中使用！
"""

from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# 数据库文件
DB_FILE = 'vulnerable_users.db'

def init_db():
    """初始化数据库"""
    # 如果数据库已存在，先删除
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')
    
    # 插入测试数据
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('user', 'user123', 'user')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'guest123', 'guest')")
    
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")

@app.route('/login', methods=['POST'])
def login():
    """
    ⚠️ 漏洞登录接口 - 直接拼接 SQL 语句
    """
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    # ⚠️ 危险！直接拼接 SQL 语句，存在注入漏洞
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    print(f"🔍 执行的 SQL: {query}")  # 调试输出
    
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return jsonify({
                "success": True,
                "message": "Login successful! 🎉",
                "user": {
                    "id": result[0],
                    "username": result[1],
                    "role": result[3]
                }
            }), 200
        else:
            return jsonify({
                "error": "Invalid credentials",
                "message": "Username or password is incorrect"
            }), 401
    
    except sqlite3.Error as e:
        conn.close()
        return jsonify({
            "error": "Database error",
            "message": str(e)
        }), 500

@app.route('/users', methods=['GET'])
def get_users():
    """查看所有用户（用于验证注入效果）"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()
    conn.close()
    
    return jsonify({
        "users": [
            {"id": u[0], "username": u[1], "role": u[2]} 
            for u in users
        ]
    })

@app.route('/login', methods=['GET'])
def login_page():
    """显示登录说明"""
    return '''
    <h1>⚠️ 有漏洞的登录接口（仅供学习）</h1>
    <p style="color: red; font-weight: bold;">此应用故意包含 SQL 注入漏洞！</p>
    
    <h2>正常登录：</h2>
    <pre>
POST /login
Content-Type: application/json

{
    "username": "admin",
    "password": "admin123"
}
    </pre>
    
    <h2>SQL 注入测试：</h2>
    <pre>
# 绕过认证
{
    "username": "' OR 1=1 --",
    "password": "xxx"
}

# 或者
{
    "username": "admin' --",
    "password": "anything"
}
    </pre>
    
    <p><a href="/users">查看所有用户</a></p>
    '''

@app.route('/')
def index():
    return '''
    <h1>⚠️ SQL 注入漏洞演示应用</h1>
    <p style="color: red; font-weight: bold;">
        警告：此应用仅用于教育目的！<br>
        包含故意设置的安全漏洞！
    </p>
    <ul>
        <li><a href="/login">登录接口说明</a></li>
        <li><a href="/users">查看所有用户</a></li>
    </ul>
    '''

if __name__ == '__main__':
    init_db()
    print("\n" + "="*50)
    print("⚠️  漏洞应用已启动 - 仅用于学习目的！")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)