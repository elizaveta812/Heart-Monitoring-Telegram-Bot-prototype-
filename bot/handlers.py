from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, MessageHandler, filters, CommandHandler, ConversationHandler

# словарь для хранения данных пользователей - потом заменю на базу данных
user_data = {}

# Определяем состояния
GENDER, AGE, SUGAR_LEVEL, CK_MB, EDIT = range(5)


async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Привет! Давайте начнем. Какой пол у человека, за чьим состоянием я буду следить? Если мужской, то поставьте 1, а если женский, то поставьте 0.')
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
    await update.message.reply_text('Какой у этого человека уровень сахара (в миллиграммах на децилитр)? Нормальным уровнем считается от 60 до 100.')
    return SUGAR_LEVEL


async def receive_sugar_level(update: Update, context: CallbackContext) -> int:
    sugar_level = update.message.text
    if not sugar_level.isdigit() or not (40 <= int(sugar_level) <= 500):
        await update.message.reply_text('Пожалуйста, введите уровень сахара в диапазоне от 40 до 500.')
        return SUGAR_LEVEL

    user_data[update.message.chat.id]['sugar_level'] = sugar_level
    await update.message.reply_text('Какой у этого человека показатель креатинкиназа МВ? Если показатель неизвестен, то поставьте любое значение от 0 до 25 - этот уровень считается нормой.')
    return CK_MB


async def finish(update: Update, context: CallbackContext) -> int:
    ck_mb = update.message.text
    if not ck_mb.isdigit() or int(ck_mb) < 0 or int(ck_mb) > 300:
        await update.message.reply_text('Пожалуйста, введите корректный показатель креатинкиназа МВ (от 0 до 300).')
        return CK_MB

    user_data[update.message.chat.id]['ck_mb'] = ck_mb
    await update.message.reply_text('Спасибо! Теперь я буду собирать данные с носимого устройства. Мне понадобятся частота сердечных сокращений, систолическое и диастолическое давление.')

    # тут должен быть код для получения данных с носимого устройства
    # после получения данных можно выполнить предсказание
    # alert = predict_heart_attack(user_data[update.message.chat.id])
    # if alert:
    #     update.message.reply_text('Внимание! Есть риск сердечного приступа.')

    return ConversationHandler.END


async def edit_data(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Выберите, что хотите редактировать:\n1. Пол\n2. Возраст\n3. Уровень сахара\n4. Показатель креатинкиназа МВ\nВведите номер соответствующего пункта.')
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

    if GENDER in context.user_data:
        user_data[update.message.chat.id]['gender'] = update.message.text
        await update.message.reply_text('Пол обновлен.')
    elif AGE in context.user_data:
        user_data[update.message.chat.id]['age'] = update.message.text
        await update.message.reply_text('Возраст обновлен.')
    elif SUGAR_LEVEL in context.user_data:
        user_data[update.message.chat.id]['sugar_level'] = update.message.text
        await update.message.reply_text('Уровень сахара обновлен.')
    elif CK_MB in context.user_data:
        user_data[update.message.chat.id]['ck_mb'] = update.message.text
        await update.message.reply_text('Показатель креатинкиназа МВ обновлен.')

    return ConversationHandler.END


# функция для создания ConversationHandler
def get_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_gender)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_age)],
            SUGAR_LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_sugar_level)],
            CK_MB: [MessageHandler(filters.TEXT & ~filters.COMMAND, finish)],
        },
        fallbacks=[MessageHandler(filters.TEXT & ~filters.COMMAND, lambda update, context: update.message.reply_text('Пожалуйста, введите корректное значение.'))],
    )
