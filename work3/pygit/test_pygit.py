import pytest
import os
import tempfile
import shutil
import hashlib
import zlib
import struct
from unittest.mock import patch, MagicMock
import sys

# 将pygit.py作为模块导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pygit


class TestHashObject:
    """测试hash_object函数 - 覆盖文件写入的多个逻辑分支"""
    
    @pytest.fixture
    def temp_git_dir(self):
        """创建临时的.git目录用于测试"""
        temp_dir = tempfile.mkdtemp()
        git_dir = os.path.join(temp_dir, '.git', 'objects')
        os.makedirs(git_dir)
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        yield temp_dir
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)
    
    def test_hash_object_with_write_creates_file(self, temp_git_dir):
        """测试分支1: write=True且文件不存在时，应创建新文件"""
        # 准备测试数据
        test_data = b"Hello, World!"
        obj_type = "blob"
        
        # 执行函数
        sha1_hash = pygit.hash_object(test_data, obj_type, write=True)
        
        # 验证返回的哈希值格式正确（40个十六进制字符）
        assert len(sha1_hash) == 40
        assert all(c in '0123456789abcdef' for c in sha1_hash)
        
        # 验证文件被创建在正确的位置
        object_path = os.path.join('.git', 'objects', sha1_hash[:2], sha1_hash[2:])
        assert os.path.exists(object_path)
        
        # 验证文件内容（应该是压缩后的数据）
        with open(object_path, 'rb') as f:
            compressed_data = f.read()
        
        # 解压并验证内容格式
        decompressed = zlib.decompress(compressed_data)
        expected_header = f"blob {len(test_data)}".encode() + b'\x00' + test_data
        assert decompressed == expected_header
    
    def test_hash_object_without_write(self, temp_git_dir):
        """测试分支2: write=False时，只计算哈希不创建文件"""
        # 准备测试数据
        test_data = b"Test content without writing"
        obj_type = "blob"
        
        # 执行函数，设置write=False
        sha1_hash = pygit.hash_object(test_data, obj_type, write=False)
        
        # 验证返回了有效的哈希值
        assert len(sha1_hash) == 40
        
        # 验证没有创建文件
        object_path = os.path.join('.git', 'objects', sha1_hash[:2], sha1_hash[2:])
        assert not os.path.exists(object_path)
        
        # 验证哈希计算的正确性
        expected_content = f"blob {len(test_data)}".encode() + b'\x00' + test_data
        expected_hash = hashlib.sha1(expected_content).hexdigest()
        assert sha1_hash == expected_hash
    
    def test_hash_object_with_existing_file(self, temp_git_dir):
        """测试分支3: 文件已存在时，不应重复写入"""
        # 准备测试数据
        test_data = b"Duplicate test"
        obj_type = "blob"
        
        # 第一次调用，创建文件
        sha1_hash = pygit.hash_object(test_data, obj_type, write=True)
        object_path = os.path.join('.git', 'objects', sha1_hash[:2], sha1_hash[2:])
        
        # 记录文件的修改时间
        first_mtime = os.path.getmtime(object_path)
        
        # 等待一小段时间确保时间戳会改变（如果文件被重写的话）
        import time
        time.sleep(0.01)
        
        # 第二次调用相同的数据
        sha1_hash2 = pygit.hash_object(test_data, obj_type, write=True)
        
        # 验证返回相同的哈希值
        assert sha1_hash == sha1_hash2
        
        # 验证文件没有被重写（修改时间应该相同）
        second_mtime = os.path.getmtime(object_path)
        assert first_mtime == second_mtime


class TestReadIndex:
    """测试read_index函数 - 覆盖错误处理的多个分支"""
    
    @pytest.fixture
    def temp_git_dir(self):
        """创建临时的.git目录"""
        temp_dir = tempfile.mkdtemp()
        git_dir = os.path.join(temp_dir, '.git')
        os.makedirs(git_dir)
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        yield temp_dir
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)
    
    def test_read_index_file_not_found(self, temp_git_dir):
        """测试分支1: index文件不存在时，返回空列表"""
        # 确保index文件不存在
        index_path = os.path.join('.git', 'index')
        if os.path.exists(index_path):
            os.remove(index_path)
        
        # 调用函数
        result = pygit.read_index()
        
        # 验证返回空列表
        assert result == []
        assert isinstance(result, list)
    
    def test_read_index_invalid_checksum(self, temp_git_dir):
        """测试分支2: index文件校验和错误时，抛出断言错误"""
        # 创建一个具有无效校验和的index文件
        index_path = os.path.join('.git', 'index')
        
        # 创建有效的index头部
        header = b'DIRC'  # 签名
        header += struct.pack('!L', 2)  # 版本号
        header += struct.pack('!L', 0)  # 条目数量为0
        
        # 计算正确的校验和
        correct_checksum = hashlib.sha1(header).digest()
        
        # 故意写入错误的校验和
        invalid_data = header + b'\x00' * 20  # 使用全0作为错误的校验和
        
        with open(index_path, 'wb') as f:
            f.write(invalid_data)
        
        # 验证抛出断言错误
        with pytest.raises(AssertionError, match="invalid index checksum"):
            pygit.read_index()
    
    def test_read_index_invalid_signature(self, temp_git_dir):
        """测试分支3: index文件签名错误时，抛出断言错误"""
        # 创建一个具有无效签名的index文件
        index_path = os.path.join('.git', 'index')
        
        # 使用错误的签名
        invalid_header = b'BAAD'  # 错误的签名（应该是DIRC）
        invalid_header += struct.pack('!L', 2)  # 版本号
        invalid_header += struct.pack('!L', 0)  # 条目数量
        
        # 添加正确的校验和
        checksum = hashlib.sha1(invalid_header).digest()
        invalid_data = invalid_header + checksum
        
        with open(index_path, 'wb') as f:
            f.write(invalid_data)
        
        # 验证抛出断言错误
        with pytest.raises(AssertionError, match="invalid index signature"):
            pygit.read_index()
    
    def test_read_index_unsupported_version(self, temp_git_dir):
        """测试分支4: index版本不支持时，抛出断言错误"""
        # 创建一个具有不支持版本号的index文件
        index_path = os.path.join('.git', 'index')
        
        # 创建头部，使用不支持的版本号3（只支持版本2）
        header = b'DIRC'  # 正确的签名
        header += struct.pack('!L', 3)  # 不支持的版本号
        header += struct.pack('!L', 0)  # 条目数量
        
        # 添加正确的校验和
        checksum = hashlib.sha1(header).digest()
        data = header + checksum
        
        with open(index_path, 'wb') as f:
            f.write(data)
        
        # 验证抛出断言错误
        with pytest.raises(AssertionError, match="unknown index version"):
            pygit.read_index()


class TestCommit:
    """测试commit函数 - 覆盖有父提交和无父提交的分支"""
    
    @pytest.fixture
    def mock_git_env(self):
        """模拟Git环境"""
        with patch('pygit.write_tree') as mock_write_tree, \
             patch('pygit.get_local_master_hash') as mock_get_master, \
             patch('pygit.hash_object') as mock_hash_object, \
             patch('pygit.write_file') as mock_write_file, \
             patch('time.mktime') as mock_mktime, \
             patch('time.localtime') as mock_localtime, \
             patch('time.timezone', -28800):  # 模拟UTC+8时区
            
            # 设置模拟返回值
            mock_write_tree.return_value = 'abc123tree'
            mock_hash_object.return_value = 'def456commit'
            mock_mktime.return_value = 1609459200.0  # 2021-01-01 00:00:00
            mock_localtime.return_value = MagicMock()
            
            yield {
                'mock_write_tree': mock_write_tree,
                'mock_get_master': mock_get_master,
                'mock_hash_object': mock_hash_object,
                'mock_write_file': mock_write_file,
                'mock_mktime': mock_mktime
            }
    
    def test_commit_without_parent(self, mock_git_env):
        """测试分支1: 首次提交（无父提交）"""
        # 设置无父提交的情况
        mock_git_env['mock_get_master'].return_value = None
        
        # 执行提交
        message = "Initial commit"
        author = "Test User <test@example.com>"
        result = pygit.commit(message, author)
        
        # 验证返回了提交哈希
        assert result == 'def456commit'
        
        # 验证hash_object被调用，并且提交内容不包含parent行
        called_args = mock_git_env['mock_hash_object'].call_args
        commit_data = called_args[0][0].decode('utf-8')
        
        # 验证提交内容的结构
        assert 'tree abc123tree' in commit_data
        assert 'parent' not in commit_data  # 首次提交不应有父提交
        assert f'author {author}' in commit_data
        assert f'committer {author}' in commit_data
        assert message in commit_data
    
    def test_commit_with_parent(self, mock_git_env):
        """测试分支2: 后续提交（有父提交）"""
        # 设置有父提交的情况
        parent_hash = 'parent123hash'
        mock_git_env['mock_get_master'].return_value = parent_hash
        
        # 执行提交
        message = "Add new feature"
        author = "Test User <test@example.com>"
        result = pygit.commit(message, author)
        
        # 验证返回了提交哈希
        assert result == 'def456commit'
        
        # 验证hash_object被调用，并且提交内容包含parent行
        called_args = mock_git_env['mock_hash_object'].call_args
        commit_data = called_args[0][0].decode('utf-8')
        
        # 验证提交内容包含父提交引用
        assert 'tree abc123tree' in commit_data
        assert f'parent {parent_hash}' in commit_data  # 应该有父提交
        assert f'author {author}' in commit_data
        assert f'committer {author}' in commit_data
        assert message in commit_data
    
    def test_commit_timezone_handling(self, mock_git_env):
        """测试分支3: 不同时区的处理"""
        # 测试西半球时区（UTC-5）
        # 在Python中，time.timezone为正数表示UTC以西
        # 在Git中，UTC-5显示为-0500
        with patch('time.timezone', 18000):  # 18000秒 = 5小时，表示UTC-5
            mock_git_env['mock_get_master'].return_value = None
            result = pygit.commit("Test message", "User <user@test.com>")
            
            called_args = mock_git_env['mock_hash_object'].call_args
            commit_data = called_args[0][0].decode('utf-8')
            
            # UTC-5在Git中显示为-0500
            assert '-0500' in commit_data
        
        # 测试东半球时区（UTC+9）  
        # 在Python中，time.timezone为负数表示UTC以东
        # 在Git中，UTC+9显示为+0900
        with patch('time.timezone', -32400):  # -32400秒 = -9小时，表示UTC+9
            mock_git_env['mock_hash_object'].reset_mock()
            result = pygit.commit("Test message", "User <user@test.com>")
            
            called_args = mock_git_env['mock_hash_object'].call_args
            commit_data = called_args[0][0].decode('utf-8')
            
            # UTC+9在Git中显示为+0900
            assert '+0900' in commit_data


if __name__ == '__main__':
    # 可以直接运行此文件进行测试
    pytest.main([__file__, '-v'])