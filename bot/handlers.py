import random
import numpy as np
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackContext, MessageHandler, filters, CommandHandler, ConversationHandler
from model import ModelHandler

# загружаем модель
model_path = "C:/Users/eliza/PycharmProjects/MFDP-Elizaveta-Zimina/models/mfdp_model.pkl"
model_handler = ModelHandler(model_path)

# словарь для хранения данных пользователей - потом заменю на базу данных
user_data = {}

# Определяем состояния
GENDER, AGE, SUGAR_LEVEL, CK_MB, EDIT = range(5)


async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Привет! Давайте начнем. Какой пол у человека, за чьим состоянием я буду следить?'
                                    ' Если мужской, то поставьте 1, а если женский, то поставьте 0.')
    return GENDER


async def receive_gender(update: Update, context: CallbackContext) -> int:
    gender = update.message.text
    if gender not in ['0', '1']:
        await update.message.reply_text('Пожалуйста, введите 0 для женского или 1 для мужского пола.')
        return GENDER

    user_data[update.message.chat.id] = {'gender': gender}
    await update.message.reply_text('Сколько этому человеку лет?')
    return AGE


async def receive_age(update: Update, context: CallbackContext) -> int:
    age = update.message.text
    if not age.isdigit() or int(age) <= 0 or int(age) > 100:
        await update.message.reply_text('Пожалуйста, введите корректный возраст.')
        return AGE

    user_data[update.message.chat.id]['age'] = age
    await update.message.reply_text('Какой у этого человека уровень сахара (в миллиграммах на децилитр)?'
                                    ' Нормальным уровнем считается от 60 до 100.')
    return SUGAR_LEVEL


async def receive_sugar_level(update: Update, context: CallbackContext) -> int:
    sugar_level = update.message.text
    if not sugar_level.isdigit() or not (40 <= int(sugar_level) <= 500):
        await update.message.reply_text('Пожалуйста, введите уровень сахара в диапазоне от 40 до 500.')
        return SUGAR_LEVEL

    user_data[update.message.chat.id]['sugar_level'] = sugar_level
    await update.message.reply_text('Какой у этого человека показатель креатинкиназа МВ? Если показатель неизвестен,'
                                    ' то поставьте любое значение от 0 до 25 - этот уровень считается нормой.')
    return CK_MB


async def finish(update: Update, context: CallbackContext) -> int:
    ck_mb = update.message.text
    if not ck_mb.isdigit() or int(ck_mb) < 0 or int(ck_mb) > 300:
        await update.message.reply_text('Пожалуйста, введите корректный показатель креатинкиназа МВ (от 0 до 300).')
        return CK_MB

    user_data[update.message.chat.id]['ck_mb'] = ck_mb
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


async def receive_edit_choice(update: Update, context: CallbackContext) -> int:
    choice = update.message.text
    if choice == '1':
        await update.message.reply_text('Введите новый пол (0 для женского, 1 для мужского):')
        return GENDER
    elif choice == '2':
        await update.message.reply_text('Введите новый возраст:')
        return AGE
    elif choice == '3':
        await update.message.reply_text('Введите новый уровень сахара:')
        return SUGAR_LEVEL
    elif choice == '4':
        await update.message.reply_text('Введите новый показатель креатинкиназа МВ:')
        return CK_MB
    else:
        await update.message.reply_text('Пожалуйста, выберите корректный номер.')
        return EDIT


# обновление данных в словаре
async def finish_edit(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat.id
    new_value = update.message.text

    # проверка на редактирование пола
    if GENDER in context.chat_data:
        if new_value not in ['0', '1']:
            await update.message.reply_text('Пожалуйста, введите 0 для женского или 1 для мужского пола.')
            return GENDER
        user_data[user_id]['gender'] = new_value
        await update.message.reply_text('Пол обновлен.')

    # проверка на редактирование возраста
    elif AGE in context.chat_data:
        if not new_value.isdigit() or not (1 <= int(new_value) <= 100):
            await update.message.reply_text('Пожалуйста, введите корректный возраст (от 1 до 100).')
            return AGE
        user_data[user_id]['age'] = new_value
        await update.message.reply_text('Возраст обновлен.')

    # проверка на редактирование уровня сахара
    elif SUGAR_LEVEL in context.chat_data:
        if not new_value.isdigit() or not (40 <= int(new_value) <= 500):
            await update.message.reply_text('Пожалуйста, введите уровень сахара в диапазоне от 40 до 500.')
            return SUGAR_LEVEL
        user_data[user_id]['sugar_level'] = new_value
        await update.message.reply_text('Уровень сахара обновлен.')

    # проверка на редактирование показателя креатинкиназа МВ
    elif CK_MB in context.chat_data:
        if not new_value.isdigit() or not (0 <= int(new_value) <= 300):
            await update.message.reply_text('Пожалуйста, введите корректный показатель креатинкиназа МВ (от 0 до 300).')
            return CK_MB
        user_data[user_id]['ck_mb'] = new_value
        await update.message.reply_text('Показатель креатинкиназа МВ обновлен.')

    return ConversationHandler.END


# функция для генерации случайных данных
def generate_random_data():
    heart_rate = random.randint(20, 200)
    systolic_pressure = random.randint(40, 230)
    diastolic_pressure = random.randint(30, 160)
    return heart_rate, systolic_pressure, diastolic_pressure


# функция для предсказания риска сердечного приступа
def predict_heart_attack(model_handler, user_data, random_data):
    # объединяем данные
    features = [
        int(user_data['age']),  # Age (int64)
        int(user_data['gender']),  # Gender (int64)
        int(random_data[0]),  # Heart rate (int64)
        int(random_data[1]),  # Systolic blood pressure (int64)
        int(random_data[2]),  # Diastolic blood pressure (int64)
        float(user_data['sugar_level']),  # Blood sugar (float64)
        float(user_data['ck_mb'])  # CK-MB (float64)
    ]

    # создаем массив с нужными типами данных
    features = np.array(features, dtype=object)  # временно создаем массив с типом object
    features[:5] = np.array(features[:5], dtype=np.int64)  # первые 5 элементов int64
    features[5:] = np.array(features[5:], dtype=np.float64)  # последние 2 элемента float64

    # преобразуем в нужный формат для модели
    features = features.reshape(1, -1)

    prediction = model_handler.predict(features)
    return prediction[0]  # возвращаем предсказание


# Обработчик для генерации данных и предсказания
async def generate_data_and_predict(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat.id
    user_info = {
        'gender': int(user_data[user_id]['gender']),
        'age': int(user_data[user_id]['age']),
        'sugar_level': float(user_data[user_id]['sugar_level']),
        'ck_mb': float(user_data[user_id]['ck_mb']),
    }

    random_data = generate_random_data()

    # Предсказание
    risk = predict_heart_attack(model_handler, user_info, random_data)

    # Формирование сообщения
    message = (
        f"Сгенерированные данные:\n"
        f"Частота сердечных сокращений: {random_data[0]} уд/мин\n"
        f"Систолическое давление: {random_data[1]} мм рт. ст.\n"
        f"Диастолическое давление: {random_data[2]} мм рт. ст.\n"
        f"Риск сердечного приступа: {'Да' if risk == 1 else 'Нет'}"
    )

    await update.message.reply_text(message)

    # предупреждение
    if risk == 1:
        await update.message.reply_text('Внимание! Есть риск сердечного приступа!')


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

    if query.data == 'generate_data':
        await generate_data_and_predict(query.message, context)


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
