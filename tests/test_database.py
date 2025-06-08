import pytest
from unittest.mock import MagicMock
from database.database import get_user, add_user, update_user


# имитация сессии базы данных
@pytest.fixture
def mock_session():
    return MagicMock()


# проверка, что метод add был вызван
def test_add_user(mock_session):
    add_user(mock_session, chat_id=12345, gender='1', age=None, sugar_level=None, ck_mb=None)
    mock_session.add.assert_called_once()


# проверка, что возвращается правильный пользователь
def test_get_user(mock_session):
    mock_user = MagicMock()
    mock_session.query.return_value.filter.return_value.first.return_value = mock_user

    user = get_user(mock_session, 12345)
    assert user == mock_user


# проверка, что метод commit был вызван
def test_update_user(mock_session):
    update_user(mock_session, 12345, gender='0', age=30)
    mock_session.commit.assert_called_once()


if __name__ == "__main__":
    pytest.main()

