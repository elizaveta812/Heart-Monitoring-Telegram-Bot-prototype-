import pytest
from unittest.mock import MagicMock, AsyncMock
from database.database import get_user, add_user, update_user
from bot.handlers import (
    start,
    receive_gender,
    receive_age,
    receive_sugar_level,
    finish,
    generate_random_data,
    predict_heart_attack,
    create_button
)


# имитация сессии базы данных
@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.mark.asyncio
async def test_start():
    update = MagicMock()
    context = MagicMock()
    update.message.reply_text = AsyncMock()

    await start(update, context)

    update.message.reply_text.assert_called_once_with(
        'Привет! Давайте начнем. Какой пол у человека, за чьим состоянием я буду следить?'
        ' Если мужской, то поставьте 1, а если женский, то поставьте 0.'
    )


@pytest.mark.asyncio
async def test_receive_gender_valid(mock_session):
    update = MagicMock()
    context = MagicMock()
    update.message.text = '1'
    update.message.chat.id = 12345
    update.message.reply_text = AsyncMock()

    # имитация работы базы данных
    get_user_mock = AsyncMock(return_value=None)
    add_user_mock = AsyncMock()
    update_user_mock = AsyncMock()

    # заменяем реальные функции на моки
    get_user = get_user_mock
    add_user = add_user_mock
    update_user = update_user_mock

    await receive_gender(update, context)

    add_user_mock.assert_called_once_with(mock_session, chat_id=12345, gender='1', age=None, sugar_level=None, ck_mb=None)
    update.message.reply_text.assert_called_once_with('Сколько этому человеку лет?')


@pytest.mark.asyncio
async def test_receive_gender_invalid():
    update = MagicMock()
    context = MagicMock()
    update.message.text = 'invalid'
    update.message.reply_text = AsyncMock()

    await receive_gender(update, context)

    update.message.reply_text.assert_called_once_with('Пожалуйста, введите 0 для женского или 1 для мужского пола.')


@pytest.mark.asyncio
async def test_receive_age_valid(mock_session):
    update = MagicMock()
    context = MagicMock()
    update.message.text = '30'
    update.message.chat.id = 12345
    update.message.reply_text = AsyncMock()

    # имитация работы базы данных
    update_user_mock = AsyncMock()
    update_user = update_user_mock

    await receive_age(update, context)

    update_user_mock.assert_called_once_with(mock_session, 12345, age=30)
    update.message.reply_text.assert_called_once_with(
        'Какой у этого человека уровень сахара (в миллиграммах на децилитр)? Нормальным уровнем считается от 60 до 100.'
    )


@pytest.mark.asyncio
async def test_receive_sugar_level_valid(mock_session):
    update = MagicMock()
    context = MagicMock()
    update.message.text = '90'
    update.message.chat.id = 12345
    update.message.reply_text = AsyncMock()

    # имитация работы базы данных
    update_user_mock = AsyncMock()
    update_user = update_user_mock

    await receive_sugar_level(update, context)

    update_user_mock.assert_called_once_with(mock_session, 12345, sugar_level=90)
    update.message.reply_text.assert_called_once_with(
        'Спасибо! Теперь мне понадобятся частота сердечных сокращений, систолическое и диастолическое давление. '
        'Поскольку я пока не могу сам собирать эти данные, мы их сгенерируем!'
    )


@pytest.mark.asyncio
async def test_receive_sugar_level_invalid():
    update = MagicMock()
    context = MagicMock()
    update.message.text = 'invalid'  # некорректный уровень сахара
    update.message.reply_text = AsyncMock()

    await receive_sugar_level(update, context)

    update.message.reply_text.assert_called_once_with('Пожалуйста, введите корректный уровень сахара'
                                                      ' (в миллиграммах на децилитр).')


@pytest.mark.asyncio
async def test_finish_valid(mock_session):
    update = MagicMock()
    context = MagicMock()
    update.message.text = '10'
    update.message.chat.id = 12345
    update.message.reply_text = AsyncMock()

    # имитация работы базы данных
    update_user_mock = AsyncMock()
    update_user = update_user_mock

    await finish(update, context)

    update_user_mock.assert_called_once_with(mock_session, 12345, ck_mb=10)
    update.message.reply_text.assert_called_once_with(
        'Спасибо! Теперь мне понадобятся частота сердечных сокращений, систолическое и диастолическое давление. '
        'Поскольку я пока не могу сам собирать эти данные, мы их сгенерируем!'
    )


def test_generate_random_data():
    random_data = generate_random_data()
    assert len(random_data) == 3


def test_predict_heart_attack():
    model_handler = MagicMock()
    user_data = {
        'age': 30,
        'gender': 1,
        'sugar_level': 90,
        'ck_mb': 10
    }
    random_data = (70, 120, 80)
    prediction = predict_heart_attack(model_handler, user_data, random_data)
    assert prediction in [0, 1]


@pytest.mark.asyncio
async def test_create_button():
    update = MagicMock()
    context = MagicMock()
    update.message.reply_text = AsyncMock()

    await create_button(update, context)

    update.message.reply_text.assert_called_once_with(
        'Нажмите кнопку, чтобы сгенерировать данные и получить предсказание.'
    )

if __name__ == "__main__":
    pytest.main()

