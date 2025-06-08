import pika
import json
import threading
import logging
from bot.model import ModelHandler

# Настройка логирования
logging.basicConfig(level=logging.INFO)


# Настройка RabbitMQ
def setup_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='ml_tasks')
    return channel


def validate_data(input_data):
    # тут что-то будет
    return True


def process_message(body):
    task_data = json.loads(body)
    input_data = task_data['input_data']
    user_id = task_data['user_id']

    # валидация данных
    if not validate_data(input_data):
        logging.warning(f"Инвалидные данные для пользователя {user_id}: {input_data}")
        return

    try:
        # выполнение предсказания
        model = ModelHandler(model_id=1, model_name="best_random_forest_model.pkl")
        prediction = model.predict(input_data)

        # запись результата
        logging.info(f"Предсказание для пользователя {user_id}: {prediction}")
    except Exception as e:
        logging.error(f"Ошибка при обработке данных для пользователя {user_id}: {e}")


def callback(ch, method, properties, body):
    # обработка сообщения в отдельном потоке
    threading.Thread(target=process_message, args=(body,)).start()
    # подтверждение сообщения после обработки
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    channel = setup_rabbitmq()
    channel.basic_consume(queue='ml_tasks', on_message_callback=callback, auto_ack=False)

    logging.info('Ожидаем сообщения...')
    channel.start_consuming()


if __name__ == "__main__":
    main()

