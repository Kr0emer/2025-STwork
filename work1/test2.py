def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


class TestBasicMath:
    
    
    def test_add_positive_numbers(self):
        assert add(2, 3) == 5
        assert add(10, 20) == 30
    
    def test_add_negative_numbers(self):
        assert add(-1, -2) == -3
        assert add(-5, 3) == -2
    
    def test_subtract(self):
        assert subtract(5, 3) == 2
        assert subtract(10, 10) == 0
        assert subtract(3, 5) == -2


def test_simple_assertion():
    assert 1 + 1 == 2
    assert "hello" != "world"
    assert True is not False


def test_list_operations():
    my_list = [1, 2, 3]
    my_list.append(4)
    assert len(my_list) == 4
    assert my_list[-1] == 4
    assert 2 in my_list


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])