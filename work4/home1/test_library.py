"""
图书管理系统 - 单元测试
"""

import pytest
from library import (
    Library, User, Book, borrow_book,
    UserNotFoundError, BookNotFoundError, 
    BookNotAvailableError, AlreadyBorrowedError
)


@pytest.fixture
def library():
    """创建测试用的图书馆实例"""
    lib = Library()
    
    # 添加用户
    lib.add_user(User("U001", "张三"))
    lib.add_user(User("U002", "李四"))
    lib.add_user(User("U003", "王五"))
    
    # 添加图书
    lib.add_book(Book("B001", "Python编程", "作者A", 3))
    lib.add_book(Book("B002", "Java核心技术", "作者B", 2))
    lib.add_book(Book("B003", "算法导论", "作者C", 0))  # 库存为0
    lib.add_book(Book("B004", "设计模式", "作者D", 1))
    
    return lib


class TestBorrowBook:
    """借书功能测试类"""
    
    def test_borrow_book_success(self, library):
        """测试1: 正常借书 - 成功情况"""
        result = borrow_book(library, "U001", "B001")
        
        # 验证返回结果
        assert result["success"] is True
        assert "张三" in result["message"]
        assert "Python编程" in result["message"]
        assert result["original_stock"] == 3
        assert result["current_stock"] == 2
        
        # 验证库存减少
        book = library.get_book("B001")
        assert book.stock == 2
        
        # 验证用户借阅记录
        user = library.get_user("U001")
        assert "B001" in user.borrowed_books
        
        print("✅ 测试1通过：正常借书成功")
    
    def test_user_not_found(self, library):
        """测试2: 用户不存在 - 异常情况"""
        with pytest.raises(UserNotFoundError) as exc_info:
            borrow_book(library, "U999", "B001")
        
        assert "用户 U999 不存在" in str(exc_info.value)
        
        # 验证库存未改变
        book = library.get_book("B001")
        assert book.stock == 3
        
        print("✅ 测试2通过：用户不存在抛出异常")
    
    def test_book_not_found(self, library):
        """测试3: 图书不存在 - 异常情况"""
        with pytest.raises(BookNotFoundError) as exc_info:
            borrow_book(library, "U001", "B999")
        
        assert "图书 B999 不存在" in str(exc_info.value)
        
        # 验证用户借阅记录未改变
        user = library.get_user("U001")
        assert "B999" not in user.borrowed_books
        
        print("✅ 测试3通过：图书不存在抛出异常")
    
    def test_book_not_available(self, library):
        """测试4: 图书库存为0 - 异常情况"""
        with pytest.raises(BookNotAvailableError) as exc_info:
            borrow_book(library, "U001", "B003")
        
        assert "库存不足" in str(exc_info.value)
        
        # 验证库存仍为0
        book = library.get_book("B003")
        assert book.stock == 0
        
        # 验证用户借阅记录未改变
        user = library.get_user("U001")
        assert "B003" not in user.borrowed_books
        
        print("✅ 测试4通过：库存不足抛出异常")
    
    def test_already_borrowed(self, library):
        """测试5: 用户已借阅该书 - 异常情况"""
        # 先成功借一次
        borrow_book(library, "U001", "B002")
        
        # 再次借同一本书应该失败
        with pytest.raises(AlreadyBorrowedError) as exc_info:
            borrow_book(library, "U001", "B002")
        
        assert "已借阅" in str(exc_info.value)
        
        # 验证库存只减少了一次
        book = library.get_book("B002")
        assert book.stock == 1
        
        # 验证借阅记录中只有一条
        user = library.get_user("U001")
        assert user.borrowed_books.count("B002") == 1
        
        print("✅ 测试5通过：重复借书抛出异常")
    
    def test_multiple_users_borrow_same_book(self, library):
        """测试6: 多个用户借同一本书 - 正常情况"""
        # 用户1借书
        result1 = borrow_book(library, "U001", "B001")
        assert result1["success"] is True
        assert result1["current_stock"] == 2
        
        # 用户2借同一本书
        result2 = borrow_book(library, "U002", "B001")
        assert result2["success"] is True
        assert result2["current_stock"] == 1
        
        # 验证最终库存
        book = library.get_book("B001")
        assert book.stock == 1
        
        # 验证两个用户都有借阅记录
        user1 = library.get_user("U001")
        user2 = library.get_user("U002")
        assert "B001" in user1.borrowed_books
        assert "B001" in user2.borrowed_books
        
        print("✅ 测试6通过：多用户借同一本书成功")
    
    def test_borrow_last_copy(self, library):
        """测试7: 借最后一本 - 边界情况"""
        # B004 只有1本库存
        result = borrow_book(library, "U001", "B004")
        
        assert result["success"] is True
        assert result["original_stock"] == 1
        assert result["current_stock"] == 0
        
        # 验证库存为0
        book = library.get_book("B004")
        assert book.stock == 0
        assert not book.is_available()
        
        # 验证第二个用户无法借阅
        with pytest.raises(BookNotAvailableError):
            borrow_book(library, "U002", "B004")
        
        print("✅ 测试7通过：借最后一本后库存为0")
    
    def test_user_borrow_multiple_books(self, library):
        """测试8: 同一用户借多本书 - 正常情况"""
        # 用户借第一本书
        result1 = borrow_book(library, "U003", "B001")
        assert result1["success"] is True
        
        # 同一用户借第二本书
        result2 = borrow_book(library, "U003", "B002")
        assert result2["success"] is True
        
        # 验证用户有两条借阅记录
        user = library.get_user("U003")
        assert len(user.borrowed_books) == 2
        assert "B001" in user.borrowed_books
        assert "B002" in user.borrowed_books
        
        # 验证两本书的库存都减少了
        book1 = library.get_book("B001")
        book2 = library.get_book("B002")
        assert book1.stock == 2
        assert book2.stock == 1
        
        print("✅ 测试8通过：用户可以借多本书")


# 额外测试：边界和特殊情况
class TestEdgeCases:
    """边界情况测试"""
    
    def test_empty_library(self):
        """测试9: 空图书馆 - 边界情况"""
        empty_lib = Library()
        
        # 没有用户
        with pytest.raises(UserNotFoundError):
            borrow_book(empty_lib, "U001", "B001")
        
        print("✅ 测试9通过：空图书馆处理正确")
    
    def test_book_stock_consistency(self, library):
        """测试10: 库存一致性 - 压力测试"""
        initial_stock = library.get_book("B001").stock
        
        # 多次借书直到库存为0
        borrowed_count = 0
        for i in range(initial_stock):
            user_id = f"U00{i+1}"
            if user_id not in library.users:
                library.add_user(User(user_id, f"用户{i+1}"))
            
            result = borrow_book(library, user_id, "B001")
            assert result["success"] is True
            borrowed_count += 1
        
        # 验证库存为0
        book = library.get_book("B001")
        assert book.stock == 0
        assert borrowed_count == initial_stock
        
        # 验证无法再借
        library.add_user(User("U999", "额外用户"))
        with pytest.raises(BookNotAvailableError):
            borrow_book(library, "U999", "B001")
        
        print("✅ 测试10通过：库存一致性验证通过")


if __name__ == "__main__":
    # 可以直接运行此文件进行测试
    pytest.main([__file__, "-v", "--tb=short"])