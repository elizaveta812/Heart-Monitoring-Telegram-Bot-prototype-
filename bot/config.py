import os
from dotenv import load_dotenv

# ��������� ���������� ��������� �� .env �����
load_dotenv()

# �������� ����� �� ���������� ���������
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ��� �������� ����� ������ ���������� ���������

