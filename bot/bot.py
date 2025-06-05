import logging
from telegram.ext import Updater
from handlers import get_conversation_handler
from config import TELEGRAM_BOT_TOKEN

# логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def main() -> None:
    updater = Updater(TELEGRAM_BOT_TOKEN)

    dispatcher = updater.dispatcher

    # определяем обработчики состояний
    conv_handler = get_conversation_handler()

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

