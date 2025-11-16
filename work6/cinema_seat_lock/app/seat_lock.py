"""
座位锁定系统模块
实现座位的锁定、解锁、超时自动释放等功能
"""
import time


class SeatLockSystem:
    """座位锁定系统类"""
    
    def __init__(self, timeout=60):
        """
        初始化座位锁定系统
        
        Args:
            timeout (int): 锁定超时时间（秒），默认60秒
        """
        self.locked_seats = {}
        self.timeout = timeout
    
    def lock(self, seat_id, user):
        """
        锁定座位
        
        Args:
            seat_id (str): 座位ID
            user (str): 用户ID
        
        Returns:
            bool: 锁定成功返回True，座位已被锁定返回False
        """
        now = time.time()
        
        # 检查座位是否已被锁定且未过期
        if seat_id in self.locked_seats:
            if self.locked_seats[seat_id]['expire'] > now:
                return False  # 座位已被占用
        
        # 锁定座位
        self.locked_seats[seat_id] = {
            'user': user,
            'expire': now + self.timeout
        }
        return True
    
    def is_locked(self, seat_id):
        """
        检查座位是否被锁定
        
        Args:
            seat_id (str): 座位ID
        
        Returns:
            bool: 已锁定返回True，未锁定或已过期返回False
        """
        now = time.time()
        
        if seat_id in self.locked_seats:
            if self.locked_seats[seat_id]['expire'] > now:
                return True  # 座位已锁定且未过期
        
        return False
    
    def unlock(self, seat_id, user):
        """
        解锁座位
        
        Args:
            seat_id (str): 座位ID
            user (str): 用户ID
        
        Returns:
            bool: 解锁成功返回True，座位未锁定或用户不匹配返回False
        """
        if seat_id not in self.locked_seats:
            return False  # 座位未锁定
        
        # 检查是否是锁定该座位的用户
        if self.locked_seats[seat_id]['user'] != user:
            return False  # 用户不匹配
        
        # 删除锁定记录
        del self.locked_seats[seat_id]
        return True
    
    def get_lock_info(self, seat_id):
        """
        获取座位锁定信息
        
        Args:
            seat_id (str): 座位ID
        
        Returns:
            dict or None: 返回锁定信息或None
        """
        now = time.time()
        
        if seat_id in self.locked_seats:
            lock_info = self.locked_seats[seat_id]
            if lock_info['expire'] > now:
                remaining_time = lock_info['expire'] - now
                return {
                    'user': lock_info['user'],
                    'remaining_time': remaining_time
                }
        
        return None
    
    def extend_lock(self, seat_id, user, extra_time=None):
        """
        延长座位锁定时间
        
        Args:
            seat_id (str): 座位ID
            user (str): 用户ID
            extra_time (int): 延长的时间（秒），默认为timeout
        
        Returns:
            bool: 延长成功返回True，否则返回False
        """
        if seat_id not in self.locked_seats:
            return False  # 座位未锁定
        
        # 检查是否是锁定该座位的用户
        if self.locked_seats[seat_id]['user'] != user:
            return False  # 用户不匹配
        
        # 检查锁是否已过期
        now = time.time()
        if self.locked_seats[seat_id]['expire'] <= now:
            return False  # 锁已过期
        
        # 延长锁定时间
        if extra_time is None:
            extra_time = self.timeout
        
        self.locked_seats[seat_id]['expire'] += extra_time
        return True
    
    def get_all_locked_seats(self):
        """
        获取所有被锁定的座位
        
        Returns:
            list: 被锁定的座位ID列表
        """
        now = time.time()
        locked = []
        
        for seat_id, lock_info in self.locked_seats.items():
            if lock_info['expire'] > now:
                locked.append(seat_id)
        
        return locked
    
    def clear_expired_locks(self):
        """
        清理所有过期的锁定记录
        
        Returns:
            int: 清理的锁定数量
        """
        now = time.time()
        expired_seats = []
        
        # 找出所有过期的座位
        for seat_id, lock_info in self.locked_seats.items():
            if lock_info['expire'] <= now:
                expired_seats.append(seat_id)
        
        # 删除过期的锁定
        for seat_id in expired_seats:
            del self.locked_seats[seat_id]
        
        return len(expired_seats)