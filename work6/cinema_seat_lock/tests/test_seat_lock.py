"""
座位锁定系统的单元测试
测试所有功能模块和边界情况
"""
import pytest
import time
from app.seat_lock import SeatLockSystem


class TestSeatLockSystem:
    """测试座位锁定系统的基本功能"""
    
    def test_lock_success(self):
        """测试用例1：成功锁定座位"""
        # 1. 准备 (Arrange)
        system = SeatLockSystem(timeout=60)
        
        # 2. 执行 (Act)
        result = system.lock("A1", "user_001")
        
        # 3. 断言 (Assert)
        assert result is True  # 期望锁定成功返回True
        assert system.is_locked("A1") is True  # 期望查询时显示已锁定
    
    def test_lock_already_locked(self):
        """测试用例2：锁定已被占用的座位"""
        system = SeatLockSystem(timeout=60)
        
        # 第一次锁定成功
        system.lock("A1", "user_001")
        
        # 第二次锁定同一座位应该失败
        result = system.lock("A1", "user_002")
        
        assert result is False
        assert system.is_locked("A1") is True
        # 验证座位仍然属于第一个用户
        lock_info = system.get_lock_info("A1")
        assert lock_info['user'] == "user_001"
    
    def test_lock_different_seats(self):
        """测试用例3：锁定不同的座位"""
        system = SeatLockSystem(timeout=60)
        
        # 锁定多个不同座位
        assert system.lock("A1", "user_001") is True
        assert system.lock("A2", "user_002") is True
        assert system.lock("B1", "user_001") is True
        
        # 验证所有座位都被锁定
        assert system.is_locked("A1") is True
        assert system.is_locked("A2") is True
        assert system.is_locked("B1") is True
    
    def test_is_locked_unlocked_seat(self):
        """测试用例4：检查未锁定的座位"""
        system = SeatLockSystem(timeout=60)
        
        # 未锁定的座位应该返回False
        assert system.is_locked("A1") is False
        assert system.is_locked("B2") is False


class TestSeatLockExpiration:
    """测试座位锁定的过期机制"""
    
    def test_lock_expire_naturally(self):
        """测试用例5：锁定自然过期"""
        system = SeatLockSystem(timeout=1)  # 设置1秒超时
        
        # 锁定座位
        system.lock("A1", "user_001")
        assert system.is_locked("A1") is True
        
        # 等待超时
        time.sleep(1.1)
        
        # 座位应该已经解锁
        assert system.is_locked("A1") is False
    
    def test_lock_and_manual_expire(self):
        """测试用例6：手动设置过期时间"""
        system = SeatLockSystem(timeout=60)
        
        # 锁定座位
        assert system.lock("A1", "user_001") is True
        
        # 手动设置为已过期
        system.locked_seats["A1"]["expire"] = time.time() - 1
        
        # 座位应该显示为未锁定
        assert system.is_locked("A1") is False
    
    def test_relock_after_expire(self):
        """测试用例7：过期后重新锁定"""
        system = SeatLockSystem(timeout=60)
        
        # 第一次锁定
        system.lock("A1", "user_001")
        
        # 手动设置为已过期
        system.locked_seats["A1"]["expire"] = time.time() - 1
        
        # 其他用户应该能够重新锁定
        result = system.lock("A1", "user_002")
        assert result is True
        assert system.is_locked("A1") is True
        
        # 验证座位现在属于user_002
        lock_info = system.get_lock_info("A1")
        assert lock_info['user'] == "user_002"


class TestSeatUnlock:
    """测试座位解锁功能"""
    
    def test_unlock_success(self):
        """测试用例8：成功解锁座位"""
        system = SeatLockSystem(timeout=60)
        
        # 锁定座位
        system.lock("A1", "user_001")
        
        # 用户解锁自己的座位
        result = system.unlock("A1", "user_001")
        
        assert result is True
        assert system.is_locked("A1") is False
    
    def test_unlock_wrong_user(self):
        """测试用例9：错误的用户尝试解锁"""
        system = SeatLockSystem(timeout=60)
        
        # user_001锁定座位
        system.lock("A1", "user_001")
        
        # user_002尝试解锁
        result = system.unlock("A1", "user_002")
        
        assert result is False  # 解锁失败
        assert system.is_locked("A1") is True  # 座位仍然锁定
    
    def test_unlock_unlocked_seat(self):
        """测试用例10：解锁未锁定的座位"""
        system = SeatLockSystem(timeout=60)
        
        # 尝试解锁未锁定的座位
        result = system.unlock("A1", "user_001")
        
        assert result is False


class TestSeatLockInfo:
    """测试获取锁定信息功能"""
    
    def test_get_lock_info_locked_seat(self):
        """测试用例11：获取已锁定座位的信息"""
        system = SeatLockSystem(timeout=60)
        
        # 锁定座位
        system.lock("A1", "user_001")
        
        # 获取锁定信息
        lock_info = system.get_lock_info("A1")
        
        assert lock_info is not None
        assert lock_info['user'] == "user_001"
        assert lock_info['remaining_time'] > 0
        assert lock_info['remaining_time'] <= 60
    
    def test_get_lock_info_unlocked_seat(self):
        """测试用例12：获取未锁定座位的信息"""
        system = SeatLockSystem(timeout=60)
        
        # 未锁定的座位
        lock_info = system.get_lock_info("A1")
        
        assert lock_info is None
    
    def test_get_lock_info_expired_seat(self):
        """测试用例13：获取已过期座位的信息"""
        system = SeatLockSystem(timeout=60)
        
        # 锁定座位并手动过期
        system.lock("A1", "user_001")
        system.locked_seats["A1"]["expire"] = time.time() - 1
        
        # 过期座位应该返回None
        lock_info = system.get_lock_info("A1")
        
        assert lock_info is None


class TestExtendLock:
    """测试延长锁定时间功能"""
    
    def test_extend_lock_success(self):
        """测试用例14：成功延长锁定时间"""
        system = SeatLockSystem(timeout=60)
        
        # 锁定座位
        system.lock("A1", "user_001")
        
        # 获取当前过期时间
        old_expire = system.locked_seats["A1"]["expire"]
        
        # 延长30秒
        result = system.extend_lock("A1", "user_001", extra_time=30)
        
        assert result is True
        # 验证过期时间增加了
        new_expire = system.locked_seats["A1"]["expire"]
        assert new_expire > old_expire
        assert abs((new_expire - old_expire) - 30) < 0.1  # 允许小误差
    
    def test_extend_lock_wrong_user(self):
        """测试用例15：错误用户尝试延长锁定"""
        system = SeatLockSystem(timeout=60)
        
        # user_001锁定座位
        system.lock("A1", "user_001")
        old_expire = system.locked_seats["A1"]["expire"]
        
        # user_002尝试延长
        result = system.extend_lock("A1", "user_002", extra_time=30)
        
        assert result is False
        # 验证过期时间未改变
        assert system.locked_seats["A1"]["expire"] == old_expire
    
    def test_extend_lock_expired_seat(self):
        """测试用例16：尝试延长已过期的锁定"""
        system = SeatLockSystem(timeout=60)
        
        # 锁定座位并手动过期
        system.lock("A1", "user_001")
        system.locked_seats["A1"]["expire"] = time.time() - 1
        
        # 尝试延长已过期的锁定
        result = system.extend_lock("A1", "user_001", extra_time=30)
        
        assert result is False


class TestGetAllLockedSeats:
    """测试获取所有锁定座位功能"""
    
    def test_get_all_locked_seats_multiple(self):
        """测试用例17：获取多个锁定座位"""
        system = SeatLockSystem(timeout=60)
        
        # 锁定多个座位
        system.lock("A1", "user_001")
        system.lock("A2", "user_002")
        system.lock("B1", "user_001")
        
        # 获取所有锁定座位
        locked_seats = system.get_all_locked_seats()
        
        assert len(locked_seats) == 3
        assert "A1" in locked_seats
        assert "A2" in locked_seats
        assert "B1" in locked_seats
    
    def test_get_all_locked_seats_empty(self):
        """测试用例18：没有锁定座位时"""
        system = SeatLockSystem(timeout=60)
        
        # 未锁定任何座位
        locked_seats = system.get_all_locked_seats()
        
        assert len(locked_seats) == 0
        assert locked_seats == []
    
    def test_get_all_locked_seats_with_expired(self):
        """测试用例19：包含过期座位时"""
        system = SeatLockSystem(timeout=60)
        
        # 锁定三个座位
        system.lock("A1", "user_001")
        system.lock("A2", "user_002")
        system.lock("B1", "user_003")
        
        # 将A2设为过期
        system.locked_seats["A2"]["expire"] = time.time() - 1
        
        # 获取锁定座位（不应包含过期的）
        locked_seats = system.get_all_locked_seats()
        
        assert len(locked_seats) == 2
        assert "A1" in locked_seats
        assert "B1" in locked_seats
        assert "A2" not in locked_seats


class TestClearExpiredLocks:
    """测试清理过期锁定功能"""
    
    def test_clear_expired_locks(self):
        """测试用例20：清理过期的锁定"""
        system = SeatLockSystem(timeout=60)
        
        # 锁定多个座位
        system.lock("A1", "user_001")
        system.lock("A2", "user_002")
        system.lock("B1", "user_003")
        
        # 将其中两个设为过期
        system.locked_seats["A1"]["expire"] = time.time() - 1
        system.locked_seats["B1"]["expire"] = time.time() - 1
        
        # 清理过期锁定
        cleared_count = system.clear_expired_locks()
        
        assert cleared_count == 2
        assert "A1" not in system.locked_seats
        assert "B1" not in system.locked_seats
        assert "A2" in system.locked_seats  # A2应该还在
    
    def test_clear_expired_locks_none_expired(self):
        """测试用例21：没有过期锁定时清理"""
        system = SeatLockSystem(timeout=60)
        
        # 锁定座位但不过期
        system.lock("A1", "user_001")
        system.lock("A2", "user_002")
        
        # 清理过期锁定
        cleared_count = system.clear_expired_locks()
        
        assert cleared_count == 0
        assert len(system.locked_seats) == 2


class TestEdgeCases:
    """测试边界情况和特殊场景"""
    
    def test_very_short_timeout(self):
        """测试用例22：非常短的超时时间"""
        system = SeatLockSystem(timeout=0.1)  # 0.1秒
        
        system.lock("A1", "user_001")
        time.sleep(0.15)
        
        assert system.is_locked("A1") is False
    
    def test_empty_seat_id(self):
        """测试用例23：空座位ID"""
        system = SeatLockSystem(timeout=60)
        
        result = system.lock("", "user_001")
        assert result is True  # 系统允许空字符串作为座位ID
        assert system.is_locked("") is True
    
    def test_same_user_multiple_seats(self):
        """测试用例24：同一用户锁定多个座位"""
        system = SeatLockSystem(timeout=60)
        
        # 同一用户锁定多个座位
        assert system.lock("A1", "user_001") is True
        assert system.lock("A2", "user_001") is True
        assert system.lock("B1", "user_001") is True
        
        locked_seats = system.get_all_locked_seats()
        assert len(locked_seats) == 3
    
    def test_unicode_seat_id(self):
        """测试用例25：Unicode字符座位ID"""
        system = SeatLockSystem(timeout=60)
        
        # 使用中文座位ID
        result = system.lock("座位A1", "用户001")
        assert result is True
        assert system.is_locked("座位A1") is True
    
    def test_special_characters_seat_id(self):
        """测试用例26：特殊字符座位ID"""
        system = SeatLockSystem(timeout=60)
        
        # 使用特殊字符
        special_ids = ["A-1", "A_1", "A.1", "A@1", "A#1"]
        
        for seat_id in special_ids:
            assert system.lock(seat_id, "user_001") is True
            assert system.is_locked(seat_id) is True


class TestConcurrentScenarios:
    """测试并发相关场景（模拟）"""
    
    def test_rapid_lock_unlock(self):
        """测试用例27：快速锁定解锁"""
        system = SeatLockSystem(timeout=60)
        
        # 快速连续操作
        for i in range(10):
            assert system.lock("A1", f"user_{i}") is True
            assert system.unlock("A1", f"user_{i}") is True
        
        # 最后座位应该是未锁定状态
        assert system.is_locked("A1") is False
    
    def test_lock_collision_simulation(self):
        """测试用例28：模拟锁定冲突"""
        system = SeatLockSystem(timeout=60)
        
        # 第一个用户锁定
        assert system.lock("A1", "user_001") is True
        
        # 模拟多个用户尝试锁定同一座位
        results = []
        for i in range(2, 6):
            results.append(system.lock("A1", f"user_00{i}"))
        
        # 所有后续尝试都应该失败
        assert all(result is False for result in results)
        
        # 座位仍属于第一个用户
        lock_info = system.get_lock_info("A1")
        assert lock_info['user'] == "user_001"


# 参数化测试示例
@pytest.mark.parametrize("seat_id,user", [
    ("A1", "user_001"),
    ("B2", "user_002"),
    ("C3", "user_003"),
    ("1A", "user_004"),
    ("2B", "user_005"),
])
def test_lock_various_seats_parametrized(seat_id, user):
    """测试用例29：参数化测试不同座位锁定"""
    system = SeatLockSystem(timeout=60)
    
    assert system.lock(seat_id, user) is True
    assert system.is_locked(seat_id) is True
    
    lock_info = system.get_lock_info(seat_id)
    assert lock_info['user'] == user


@pytest.mark.parametrize("timeout", [1, 5, 10, 30, 60, 120])
def test_different_timeout_values(timeout):
    """测试用例30：参数化测试不同超时值"""
    system = SeatLockSystem(timeout=timeout)
    
    assert system.timeout == timeout
    
    # 锁定座位
    system.lock("A1", "user_001")
    lock_info = system.get_lock_info("A1")
    
    # 剩余时间应该接近timeout值
    assert lock_info['remaining_time'] <= timeout
    assert lock_info['remaining_time'] > timeout - 1