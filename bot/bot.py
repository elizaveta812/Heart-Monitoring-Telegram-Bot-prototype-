import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from handlers import get_conversation_handler
from config import TELEGRAM_BOT_TOKEN

# логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # определяем обработчики состояний
    conv_handler = get_conversation_handler()
    application.add_handler(conv_handler)

    # запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()
