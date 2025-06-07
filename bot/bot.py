import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from handlers import get_conversation_handler, button_handler
from config import TELEGRAM_BOT_TOKEN
from database.database import init_db

# логирование
logging.basicConfig(
    filename='my_bot.log',  # имя файла для логов
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def main() -> None:
    # инициализация базы данных
    session = init_db()

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # определяем обработчики состояний
    conv_handler = get_conversation_handler()
    application.add_handler(conv_handler)

    # обработчик нажатий кнопок
    application.add_handler(CallbackQueryHandler(button_handler))

    # запуск бота
    logging.info('Бот запущен')
    application.run_polling()

    # закрытие сессии базы данных
    session.close()
    logging.info('Сессия базы данных закрыта')


if __name__ == '__main__':
    main()
