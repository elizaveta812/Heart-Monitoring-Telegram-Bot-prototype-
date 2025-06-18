import random
import logging
import numpy as np
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackContext, MessageHandler, filters, CommandHandler, ConversationHandler
from model import SingletonModelHandler
from database.database import init_db, add_user, get_user, update_user

# загружаем модель только один раз с помощью синглтона
model_path = "C:/Users/eliza/PycharmProjects/MFDP-Elizaveta-Zimina/models/best_random_forest_model.pkl"
model_handler = SingletonModelHandler(model_path)

# инициализация базы данных
session = init_db()


# Объявляю класс пользователей со всеми их признаками
class User:
    def __init__(self, user_id, gender=None, age=None, sugar_level=None, ck_mb=None):
        self.user_id = user_id
        self.gender = gender
        self.age = age
        self.sugar_level = sugar_level
        self.ck_mb = ck_mb

    def update_gender(self, gender):
        self.gender = gender

    def update_age(self, age):
        self.age = age

    def update_sugar_level(self, sugar_level):
        self.sugar_level = sugar_level

    def update_ck_mb(self, ck_mb):
        self.ck_mb = ck_mb


# Определяю состояния
GENDER, AGE, SUGAR_LEVEL, CK_MB, EDIT = range(5)

# Словарь для временного хранения пользователей, чтобы не обращаться каждый раз к базе данных
users = {}


# Начало работы
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Привет! Давайте начнем. Какой пол у человека, за чьим состоянием я буду следить?'
                                    ' Если мужской, то поставьте 1, а если женский, то поставьте 0.')
    return GENDER


# Получаем пол
async def receive_gender(update: Update, context: CallbackContext) -> int:
    gender = update.message.text
    if gender not in ['0', '1']:
        await update.message.reply_text('Пожалуйста, введите 0 для женского или 1 для мужского пола.')
        return GENDER

    user_id = update.message.chat.id
    if user_id not in users:
        users[user_id] = User(user_id)

    users[user_id].update_gender(gender)

    await update.message.reply_text('Сколько этому человеку лет?')
    return AGE


# Получаем возраст
async def receive_age(update: Update, context: CallbackContext) -> int:
    age = update.message.text
    if not age.isdigit() or int(age) <= 0 or int(age) > 100:
        await update.message.reply_text('Пожалуйста, введите корректный возраст.')
        return AGE

    user_id = update.message.chat.id
    users[user_id].update_age(int(age))
    await update.message.reply_text('Какой у этого человека уровень сахара (в миллиграммах на децилитр)?'
                                    ' Нормальным уровнем считается от 60 до 100.')
    return SUGAR_LEVEL


# Получаем уровень сахара
async def receive_sugar_level(update: Update, context: CallbackContext) -> int:
    sugar_level = update.message.text
    if not sugar_level.isdigit() or not (40 <= int(sugar_level) <= 500):
        await update.message.reply_text('Пожалуйста, введите уровень сахара в диапазоне от 40 до 500.')
        return SUGAR_LEVEL

    user_id = update.message.chat.id
    users[user_id].update_sugar_level(float(sugar_level))
    await update.message.reply_text('Какой у этого человека показатель креатинкиназа МВ? Если показатель неизвестен,'
                                    ' то поставьте любое значение от 0 до 25 - этот уровень считается нормой.')
    return CK_MB


# Получаем креатинкиназа мв и заканчиваем работу
async def finish(update: Update, context: CallbackContext) -> int:
    ck_mb = update.message.text
    if not ck_mb.isdigit() or int(ck_mb) < 0 or int(ck_mb) > 300:
        await update.message.reply_text('Пожалуйста, введите корректный показатель креатинкиназа МВ (от 0 до 300).')
        return CK_MB

    user_id = update.message.chat.id
    users[user_id].update_ck_mb(float(ck_mb))
    await update.message.reply_text(
        'Спасибо! Теперь мне понадобятся частота сердечных сокращений, систолическое и диастолическое давление.'
        ' Поскольку я пока не могу сам собирать эти данные, мы их сгенерируем!'
    )

    # показ кнопки для генерации данных
    await create_button(update, context)

    # тут в идеале должен быть код для получения данных с носимого устройства
    # после получения данных можно выполнить предсказание
    # alert = predict_heart_attack(user_data[update.message.chat.id])
    # if alert:
    #     update.message.reply_text('Внимание! Есть риск сердечного приступа.')

    return ConversationHandler.END


async def edit_data(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        'Команда /edit позволяет вам изменить ранее введенные данные, такие как:\n'
        '1. Пол\n'
        '2. Возраст\n'
        '3. Уровень сахара\n'
        '4. Показатель креатинкиназа МВ\n'
        'Выберите, что хотите редактировать, введя номер соответствующего пункта.'
    )
    return EDIT


# Возможность редактировать введенные данные
async def receive_edit_choice(update: Update, context: CallbackContext) -> int:
    choice = update.message.text
    if choice == '1':
        await update.message.reply_text('Введите новый пол (0 для женского, 1 для мужского):')
        context.chat_data['edit_field'] = 'gender'
        return GENDER
    elif choice == '2':
        await update.message.reply_text('Введите новый возраст:')
        context.chat_data['edit_field'] = 'age'
        return AGE
    elif choice == '3':
        await update.message.reply_text('Введите новый уровень сахара:')
        context.chat_data['edit_field'] = 'sugar_level'
        return SUGAR_LEVEL
    elif choice == '4':
        await update.message.reply_text('Введите новый показатель креатинкиназа МВ:')
        context.chat_data['edit_field'] = 'ck_mb'
        return CK_MB
    else:
        await update.message.reply_text('Пожалуйста, выберите корректный номер.')
        return EDIT


# обновление данных
async def finish_edit(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat.id
    new_value = update.message.text

    # Получаем пользователя из словаря
    user = users.get(user_id)
    if not user:
        await update.message.reply_text('Пользователь не найден. Пожалуйста, начните заново.')
        return ConversationHandler.END

    # Проверка на редактирование пола
    if context.chat_data.get('edit_field') == 'gender':
        if new_value not in ['0', '1']:
            await update.message.reply_text('Пожалуйста, введите 0 для женского или 1 для мужского пола.')
            return GENDER
        user.update_gender(new_value)
        await update.message.reply_text('Пол обновлен.')

    # Проверка на редактирование возраста
    elif context.chat_data.get('edit_field') == 'age':
        if not new_value.isdigit() or not (1 <= int(new_value) <= 100):
            await update.message.reply_text('Пожалуйста, введите корректный возраст (от 1 до 100).')
            return AGE
        user.update_age(int(new_value))
        await update.message.reply_text('Возраст обновлен.')

    # Проверка на редактирование уровня сахара
    elif context.chat_data.get('edit_field') == 'sugar_level':
        if not new_value.isdigit() or not (40 <= int(new_value) <= 500):
            await update.message.reply_text('Пожалуйста, введите уровень сахара в диапазоне от 40 до 500.')
            return SUGAR_LEVEL
        user.update_sugar_level(float(new_value))
        await update.message.reply_text('Уровень сахара обновлен.')

    # Проверка на редактирование показателя креатинкиназа МВ
    elif context.chat_data.get('edit_field') == 'ck_mb':
        if not new_value.isdigit() or not (0 <= int(new_value) <= 300):
            await update.message.reply_text('Пожалуйста, введите корректный показатель креатинкиназа МВ (от 0 до 300).')
            return CK_MB
        user.update_ck_mb(float(new_value))
        await update.message.reply_text('Показатель креатинкиназа МВ обновлен.')

    # Сохраняем изменения в базе данных
    update_user(session, user_id, gender=user.gender, age=user.age, sugar_level=user.sugar_level, ck_mb=user.ck_mb)

    return ConversationHandler.END


# функция для генерации случайных данных
def generate_random_data():
    heart_rate = random.randint(50, 160)
    systolic_pressure = random.randint(50, 200)
    diastolic_pressure = random.randint(40, 150)
    return heart_rate, systolic_pressure, diastolic_pressure


# функция для предсказания риска сердечного приступа
def predict_heart_attack(model_handler, user_data, random_data):
    try:
        # объединяем данные
        features = [
            int(user_data['age']),
            int(user_data['gender']),
            int(random_data[0]),
            int(random_data[1]),
            int(random_data[2]),
            float(user_data['sugar_level']),
            float(user_data['ck_mb']),
        ]

        logging.info("Функция predict_heart_attack: входные данные %s", features)

        features = np.array(features, dtype=object)
        features[:5] = np.array(features[:5], dtype=np.int64)
        features[5:] = np.array(features[5:], dtype=np.float64)

        features = features.reshape(1, -1)

        prediction = model_handler.predict(features)
        logging.info("Предсказание: %s", prediction)
        return prediction[0]
    except Exception as e:
        logging.error("Error in predict_heart_attack: %s", e)
        raise


# Обработчик для генерации данных и предсказания
async def generate_data_and_predict(user_id, context: CallbackContext) -> None:
    try:
        logging.info("Получение данных пользователя для ID: %s", user_id)

        # Получаем данные пользователя из временного хранилища
        user = users.get(user_id)
        if not user:
            await context.bot.send_message(chat_id=user_id, text='Пользователь не найден. Пожалуйста, введите данные заново.')
            return

        user_info = user

        logging.info("Данные пользователя: %s", user_info)

        random_data = generate_random_data()
        logging.info("Сгенерированные случайные данные: %s", random_data)

        # Предсказание
        risk = predict_heart_attack(model_handler, user_info, random_data)
        logging.info("Результат предсказания: %s", risk)

        # Формирование сообщения
        message = (
            f"Сгенерированные данные:\n"
            f"Частота сердечных сокращений: {random_data[0]} уд/мин\n"
            f"Систолическое давление: {random_data[1]} мм рт. ст.\n"
            f"Диастолическое давление: {random_data[2]} мм рт. ст.\n"
            f"Риск сердечного приступа: {'Да' if risk == 1 else 'Нет'}"
        )

        await context.bot.send_message(chat_id=user_id, text=message)

        # предупреждение
        if risk == 1:
            await context.bot.send_message(chat_id=user_id, text='Внимание! Есть риск сердечного приступа!')
    except Exception as e:
        logging.error("Error in generate_data_and_predict: %s", e)
        await context.bot.send_message(chat_id=user_id, text='Произошла ошибка при обработке данных.')


# добавление кнопки для генерации данных
async def create_button(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Сгенерировать данные", callback_data='generate_data')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Нажмите кнопку, чтобы сгенерировать данные и получить предсказание.',
                                    reply_markup=reply_markup)


# обработчик нажатия кнопки
async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    logging.info("Button pressed: %s", query.data)

    if query.data == 'generate_data':
        user_id = query.from_user.id  # Получаем ID пользователя из объекта CallbackQuery
        await generate_data_and_predict(user_id, context)


# функция для создания ConversationHandler
def get_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("edit", edit_data)],
        states={
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_gender)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_age)],
            SUGAR_LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_sugar_level)],
            CK_MB: [MessageHandler(filters.TEXT & ~filters.COMMAND, finish)],
            EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_edit_choice)],
        },
        fallbacks=[MessageHandler(filters.TEXT & ~filters.COMMAND, lambda update, context: update.message.reply_text(
            'Пожалуйста, введите корректное значение.'))],
    )
