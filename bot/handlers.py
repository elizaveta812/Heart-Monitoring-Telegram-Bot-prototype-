from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Filters, CommandHandler, ConversationHandler

# ������� ��� �������� ������ ������������� - ����� ������ �� ���� ������
user_data = {}

# ���������� ���������
GENDER, AGE, SUGAR_LEVEL, CK_MB = range(4)

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('������! ������� ������. ����� ��� � ��������, �� ���� ���������� � ���� �������? ���� �������, �� ��������� 1, � ���� �������, �� ��������� 0.')
    return GENDER

def receive_gender(update: Update, context: CallbackContext) -> int:
    gender = update.message.text
    if gender not in ['0', '1']:
        update.message.reply_text('����������, ������� 0 ��� �������� ��� 1 ��� �������� ����.')
        return GENDER

    user_data[update.message.chat.id] = {'gender': gender}
    update.message.reply_text('������� ����� �������� ���?')
    return AGE

def receive_age(update: Update, context: CallbackContext) -> int:
    age = update.message.text
    if not age.isdigit() or int(age) <= 0:
        update.message.reply_text('����������, ������� ���������� ������� (������������� �����).')
        return AGE

    user_data[update.message.chat.id]['age'] = age
    update.message.reply_text('����� � ����� �������� ������� ������ (� ������������ �� ��������)? ���������� ������� ��������� 60-100.')
    return SUGAR_LEVEL

def receive_sugar_level(update: Update, context: CallbackContext) -> int:
    sugar_level = update.message.text
    if not sugar_level.isdigit() or not (40 <= int(sugar_level) <= 500):
        update.message.reply_text('����������, ������� ������� ������ � ��������� �� 40 �� 500.')
        return SUGAR_LEVEL

    user_data[update.message.chat.id]['sugar_level'] = sugar_level
    update.message.reply_text('����� � ��� ���������� ������������� ��? ���� ���������� ����������, �� ��������� ����� �������� �� 0 �� 25 - ���� ������� ��������� ������.')
    return CK_MB

def finish(update: Update, context: CallbackContext) -> int:
    ck_mb = update.message.text
    if not ck_mb.isdigit() or int(ck_mb) < 0 or int(ck_mb) > 300:
        update.message.reply_text('����������, ������� ���������� ���������� ������������� �� (�� 0 �� 300).')
        return CK_MB

    user_data[update.message.chat.id]['ck_mb'] = ck_mb
    update.message.reply_text('�������! ������ � ���� �������� ������ � �������� ����������. ��� ����������� ������� ��������� ����������, ������������� � �������������� ��������.')

    # ��� ������ ���� ��� ��� ��������� ������ � �������� ����������

    # ����� ��������� ������ ����� ��������� ������������
    # alert = predict_heart_attack(user_data[update.message.chat.id])
    # if alert:
    #     update.message.reply_text('��������! ���� ���� ���������� ��������.')

    return ConversationHandler.END

# ������� ��� �������� ConversationHandler
def get_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENDER: [MessageHandler(Filters.text & ~Filters.command, receive_gender)],
            AGE: [MessageHandler(Filters.text & ~Filters.command, receive_age)],
            SUGAR_LEVEL: [MessageHandler(Filters.text & ~Filters.command, receive_sugar_level)],
            CK_MB: [MessageHandler(Filters.text & ~Filters.command, finish)],
        },
        fallbacks=[MessageHandler(Filters.text & ~Filters.command, lambda update, context: update.message.reply_text('����������, ������� ���������� ��������.'))],
    )

