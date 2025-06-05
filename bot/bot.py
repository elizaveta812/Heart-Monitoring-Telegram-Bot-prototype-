import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from config import TELEGRAM_BOT_TOKEN

# логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# словарь для хранения данных пользователей
user_data = {}

# определяем состояния
GENDER, AGE, SUGAR_LEVEL, CK_MB = range(4)

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Привет! Давайте начнем. Какой пол у человека, за чьим состоянием я буду следить? Если мужской то поставьте 1, а если женский, то поставьте 0)')
    return GENDER

def receive_gender(update: Update, context: CallbackContext) -> int:
    gender = update.message.text
    if gender not in ['0', '1']:
        update.message.reply_text('Пожалуйста, введите 0 для женского или 1 для мужского пола.')
        return GENDER

    user_data[update.message.chat.id] = {'gender': gender}
    update.message.reply_text('Сколько этому человеку лет?')
    return AGE

def receive_age(update: Update, context: CallbackContext) -> int:
    age = update.message.text
    if not age.isdigit() or int(age) <= 0:
        update.message.reply_text('Пожалуйста, введите корректный возраст (положительное число).')
        return AGE

    user_data[update.message.chat.id]['age'] = age
    update.message.reply_text('Какой у этого человека уровень сахара (в миллиграммах на децилитр)? Нормальным уровнем считается 60-100.')
    return SUGAR_LEVEL

def receive_sugar_level(update: Update, context: CallbackContext) -> int:
    sugar_level = update.message.text
    if not sugar_level.isdigit() or not (40 <= int(sugar_level) <= 500):
        update.message.reply_text('Пожалуйста, введите уровень сахара в диапазоне от 40 до 500 в миллиграммах на децилитр.')
        return SUGAR_LEVEL

    user_data[update.message.chat.id]['sugar_level'] = sugar_level
    update.message.reply_text('Какой у вас показатель креатинкиназа МВ? Если показатель неизвестен, то поставьте любое значение от 0 до 25 - этот уровень считается нормой.')
    return CK_MB

def finish(update: Update, context: CallbackContext) -> int:
    ck_mb = update.message.text
    if not ck_mb.isdigit() or int(ck_mb) < 0 or int(ck_mb) > 25:
        update.message.reply_text('Пожалуйста, введите корректный показатель креатинкиназа МВ - от 0 до 300 (верхняя граница).')
        return CK_MB

    user_data[update.message.chat.id]['ck_mb'] = ck_mb
    update.message.reply_text('Спасибо! Теперь я буду собирать данные с носимого устройства. Мне понадобятся частота сердечных сокращений, систолическое и диастолическое давление.')

    # тут должен быть код для получения данных с носимого устройства

    # после получения данных можно выполнить предсказание
    # alert = predict_heart_attack(user_data[update.message.chat.id])
    # if alert:
    #     update.message.reply_text('Внимание! Есть риск сердечного приступа.')

    return ConversationHandler.END

def main() -> None:
    updater = Updater(TELEGRAM_BOT_TOKEN)

    dispatcher = updater.dispatcher

    # определяем обработчики состояний
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENDER: [MessageHandler(Filters.text & ~Filters.command, receive_gender)],
            AGE: [MessageHandler(Filters.text & ~Filters.command, receive_age)],
            SUGAR_LEVEL: [MessageHandler(Filters.text & ~Filters.command, receive_sugar_level)],
            CK_MB: [MessageHandler(Filters.text & ~Filters.command, finish)],
        },
        fallbacks=[MessageHandler(Filters.text & ~Filters.command, lambda update, context: update.message.reply_text('Пожалуйста, введите корректное значение.'))],

    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

