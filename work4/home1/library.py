"""
图书管理系统 - 借书功能实现
"""

class LibraryException(Exception):
    """图书馆异常基类"""
    pass

class UserNotFoundError(LibraryException):
    """用户不存在异常"""
    pass

class BookNotFoundError(LibraryException):
    """图书不存在异常"""
    pass

class BookNotAvailableError(LibraryException):
    """图书不可借异常"""
    pass

class AlreadyBorrowedError(LibraryException):
    """已借阅该书异常"""
    pass


class Book:
    """图书类"""
    def __init__(self, book_id, title, author, stock):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.stock = stock  # 库存数量
    
    def is_available(self):
        """检查图书是否可借"""
        return self.stock > 0
    
    def borrow(self):
        """借出图书"""
        if self.stock > 0:
            self.stock -= 1
            return True
        return False
    
    def return_book(self):
        """归还图书"""
        self.stock += 1


class User:
    """用户类"""
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.borrowed_books = []  # 已借阅的图书ID列表
    
    def has_borrowed(self, book_id):
        """检查是否已借阅该书"""
        return book_id in self.borrowed_books
    
    def add_borrowed_book(self, book_id):
        """添加借阅记录"""
        self.borrowed_books.append(book_id)
    
    def remove_borrowed_book(self, book_id):
        """移除借阅记录"""
        if book_id in self.borrowed_books:
            self.borrowed_books.remove(book_id)


class Library:
    """图书馆类"""
    def __init__(self):
        self.users = {}  # {user_id: User}
        self.books = {}  # {book_id: Book}
    
    def add_user(self, user):
        """添加用户"""
        self.users[user.user_id] = user
    
    def add_book(self, book):
        """添加图书"""
        self.books[book.book_id] = book
    
    def get_user(self, user_id):
        """获取用户"""
        return self.users.get(user_id)
    
    def get_book(self, book_id):
        """获取图书"""
        return self.books.get(book_id)


def borrow_book(library, user_id, book_id):
    """
    借书功能
    
    Args:
        library: Library对象
        user_id: 用户ID
        book_id: 图书ID
    
    Returns:
        dict: 包含借书结果的字典
        
    Raises:
        UserNotFoundError: 用户不存在
        BookNotFoundError: 图书不存在
        BookNotAvailableError: 图书不可借（库存为0）
        AlreadyBorrowedError: 用户已借阅该书
    """
    
    # 1. 检查用户是否存在
    user = library.get_user(user_id)
    if user is None:
        raise UserNotFoundError(f"用户 {user_id} 不存在")
    
    # 2. 检查图书是否存在
    book = library.get_book(book_id)
    if book is None:
        raise BookNotFoundError(f"图书 {book_id} 不存在")
    
    # 3. 检查用户是否已借阅该书
    if user.has_borrowed(book_id):
        raise AlreadyBorrowedError(f"用户 {user.name} 已借阅《{book.title}》")
    
    # 4. 检查图书是否可借
    if not book.is_available():
        raise BookNotAvailableError(f"图书《{book.title}》库存不足，无法借阅")
    
    # 5. 借书操作
    original_stock = book.stock
    book.borrow()
    user.add_borrowed_book(book_id)
    
    return {
        "success": True,
        "message": f"{user.name} 成功借阅《{book.title}》",
        "user": user.name,
        "book": book.title,
        "original_stock": original_stock,
        "current_stock": book.stock
    }