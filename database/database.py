from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# базовый класс для моделей
Base = declarative_base()


# модель пользователя
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True, nullable=False)  # ID чата Telegram
    gender = Column(Integer)  # 0 для женского, 1 для мужского
    age = Column(Integer)
    sugar_level = Column(Float)
    ck_mb = Column(Float)


# функция для инициализации базы данных
def init_db():
    # Получаем URL для подключения к базе данных из переменных окружения
    db_url = os.getenv('DATABASE_URL', 'sqlite:///users.db')  # Замените на ваш URL
    engine = create_engine(db_url)

    # Создаем все таблицы
    Base.metadata.create_all(engine)

    # Создаем сессию
    Session = sessionmaker(bind=engine)
    return Session()


# функции для работы с данными
def add_user(session, chat_id, gender, age, sugar_level, ck_mb):
    user = User(chat_id=chat_id, gender=gender, age=age, sugar_level=sugar_level, ck_mb=ck_mb)
    session.add(user)
    session.commit()


def get_user(session, chat_id):
    return session.query(User).filter_by(chat_id=chat_id).first()


def update_user(session, chat_id, **kwargs):
    user = get_user(session, chat_id)
    if user:
        for key, value in kwargs.items():
            setattr(user, key, value)
        session.commit()


def delete_user(session, chat_id):
    user = get_user(session, chat_id)
    if user:
        session.delete(user)
        session.commit()
