import logging
import paramiko
import os
import re
from pathlib import Path
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import psycopg2
from psycopg2 import Error

from dotenv import load_dotenv
load_dotenv()
token = os.getenv('TOKEN')
rm_host = os.getenv('RM_HOST')
rm_port = os.getenv('RM_PORT')
rm_user = os.getenv('RM_USER')
rm_password = os.getenv('RM_PASSWORD')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_database = os.getenv('DB_DATABASE')
db_repl_user = os.getenv('DB_REPL_USER')
db_repl_password = os.getenv('DB_REPL_PASSWORD')
db_repl_host = os.getenv('DB_REPL_HOST')
db_repl_port = os.getenv('DB_REPL_PORT')
phone_numbers_global = ""
emails_global = ""

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')
    update.message.reply_text(db_host)

def helpCommand(update: Update, context):
    update.message.reply_text('Help!')

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров:')
    return 'findPhoneNumbers'

def findPhoneNumbers(update: Update, context):
    global phone_numbers_global
    user_input = update.message.text
    phoneNumRegex = re.compile(r'(8|\+7)(\d{3}|\(\d{3}\)| \d{3} | \(\d{3}\) |-\d{3}-)'
                               r'(\d{3})(\d{2}| \d{2} |-\d{2}-)(\d{2})')
    phoneNumberList = phoneNumRegex.findall(user_input)
    if not phoneNumberList:
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END
    phoneNumbers = ''
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i + 1}. {"".join(phoneNumberList[i])}\n'
        phone_numbers_global = phoneNumbers
    update.message.reply_text(phoneNumbers)
    update.message.reply_text('Введите ключевое слово "Сохранить" для сохранения в бд')
    return 'findPhoneNumbersDB'

def findPhoneNumbersDB(update: Update, context):
    global phone_numbers_global
    user_input = update.message.text
    if (user_input == "Сохранить" and phone_numbers_global != ""):
        phone_numbers = phone_numbers_global.split("\n")[:-1]
        phone_numbers_global = ""
        connection = None
        try:
            connection = psycopg2.connect(user=db_user,
                                          password=db_password,
                                          host=db_host,
                                          port=db_port,
                                          database=db_database)
                                          
            cursor = connection.cursor()
            for phone in phone_numbers:
                ph = str(phone.split(". ")[1])
                cursor.execute("INSERT INTO phone_numbers (phone_number) VALUES (" + ph + ");")
            connection.commit()
            update.message.reply_text("Данные записаны")
        except (Exception, Error) as error:
            update.message.reply_text("Ошибка при работе с PostgreSQL: %s" % str(error), parse_mode='None')
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
                return ConversationHandler.END
    else:
        return ConversationHandler.END

def findEmailNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска emails:')
    return 'findEmailNumbers'

def findEmailNumbers(update: Update, context):
    global emails_global
    user_input = update.message.text
    phoneNumRegex = re.compile(r'(\w+)(@)(\w+)(\.)(\w+)')
    phoneNumberList = phoneNumRegex.findall(user_input)
    if not phoneNumberList:
        update.message.reply_text('Emails не найдены')
        return ConversationHandler.END
    phoneNumbers = ''
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i + 1}. {"".join(phoneNumberList[i])}\n'
        emails_global = phoneNumbers
    update.message.reply_text(phoneNumbers)
    update.message.reply_text('Введите ключевое слово "Сохранить" для сохранения в бд')
    return 'findEmailNumbersDB'

def findEmailNumbersDB(update: Update, context):
    global emails_global
    user_input = update.message.text
    if (user_input == "Сохранить" and emails_global != ""):
        emails = emails_global.split("\n")[:-1]
        emails_global = ""
        connection = None
        try:
            connection = psycopg2.connect(user=db_user,
                                          password=db_password,
                                          host=db_host,
                                          port=db_port,
                                          database=db_database)
            
            cursor = connection.cursor()
            for email in emails:
                em = str(email.split(". ")[1])
                cursor.execute("INSERT INTO emails (email) VALUES ('" + em + "');")
            connection.commit()
            update.message.reply_text("Данные записаны")
            return ConversationHandler.END
        except (Exception, Error) as error:
            update.message.reply_text("Ошибка при работе с PostgreSQL: %s" % str(error), parse_mode='None')
            return ConversationHandler.END
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
    else:
        return ConversationHandler.END

def findPasswordNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для проверки сложности пароля:')
    return 'findPasswordNumbers'

def findPasswordNumbers(update: Update, context):
    user_input = update.message.text
    phoneNumRegex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()]).{8,}$')
    phoneNumberList = phoneNumRegex.findall(user_input)
    if not phoneNumberList:
        update.message.reply_text('Пароль простой')
        return ConversationHandler.END
    else:
        update.message.reply_text('Пароль сложный')
        return ConversationHandler.END


def set_apt_list_grep(update: Update, context):
    update.message.reply_text('Введите название пакета')
    return 'get_apt_list_grep'

def get_apt_list_grep(update: Update, context):
    user_input = update.message.text
    update.message.reply_text(get_command('apt list | grep '+user_input+' | head -n 10'))
    return ConversationHandler.END

def get_command(command, hostname=rm_host, username=rm_user, password=rm_password, port=rm_port):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=hostname, username=username, password=password, port=int(port))
        stdin, stdout, stderr = client.exec_command(command)
        data = stdout.read() + stderr.read()
        client.close()
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        return(data)
    except:
        return("Ошибка подключения.")

def get_release(update: Update, context):
    update.message.reply_text(get_command('lsb_release -a'))
def get_uname(update: Update, context):
    update.message.reply_text(get_command('uname -a'))
def get_uptime(update: Update, context):
    update.message.reply_text(get_command('uptime'))
def get_df(update: Update, context):
    update.message.reply_text(get_command('df'))
def get_free(update: Update, context):
    update.message.reply_text(get_command('free -h'))
def get_mpstat(update: Update, context):
    update.message.reply_text(get_command('mpstat'))
def get_w(update: Update, context):
    update.message.reply_text(get_command('w'))
def get_auths(update: Update, context):
    update.message.reply_text(get_command('last -n 10'))
def get_critical(update: Update, context):
    update.message.reply_text(get_command('journalctl -p crit -n 5'))
def get_ps(update: Update, context):
    update.message.reply_text(get_command('ps'))
def get_ss(update: Update, context):
    update.message.reply_text(get_command('ss | head -n 20'))
def get_apt_list(update: Update, context):
    update.message.reply_text(get_command('apt list | head -n 20'))
def get_services(update: Update, context):
    update.message.reply_text(get_command('service --status-all | grep +'))
def get_repl_logs(update: Update, context):
    try:
        files = os.listdir('/var/log/postgresql/')
        pattern = re.compile(r'^postgresql-\d{4}-\d{2}-\d{2}_\d{6}\.log$')
        filtered_files = [file for file in files if pattern.match(file)]
        filtered_files.sort(reverse=True)
        if filtered_files:
            with open('/var/log/postgresql/' + filtered_files[0], 'r') as file:
                lines = [next(file) for _ in range(20)]
                text = ""
                for line in lines:
                    text += line + "\n"
                update.message.reply_text(text)
    except (Exception, Error) as error:
        update.message.reply_text("Ошибка: " + str(error))
def get_emails(update: Update, context):
    connection = None
    try:
        connection = psycopg2.connect(user=db_user,
                                      password=db_password,
                                      host=db_host,
                                      port=db_port,
                                      database=db_database)


        cursor = connection.cursor()
        cursor.execute("SELECT email FROM emails;")
        data = cursor.fetchall()
        text = ""
        for row in data:
            text += "".join(row) + "\n"
        update.message.reply_text(text)
    except (Exception, Error) as error:
        update.message.reply_text("Ошибка при работе с PostgreSQL: %s" % str(error), parse_mode='None')
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
def get_phone_numbers(update: Update, context):
    connection = None
    try:
        connection = psycopg2.connect(user=db_user,
                                      password=db_password,
                                      host=db_host,
                                      port=db_port,
                                      database=db_database)

        cursor = connection.cursor()
        cursor.execute("SELECT phone_number FROM phone_numbers;")
        data = cursor.fetchall()
        text = ""
        for row in data:
            text += "".join(row) + "\n"
        update.message.reply_text(text)
    except (Exception, Error) as error:
        update.message.reply_text("Ошибка при работе с PostgreSQL: %s" % str(error), parse_mode='None')
    finally:
        if connection is not None:
            cursor.close()
            connection.close()


def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def main():
    updater = Updater(token, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'findPhoneNumbersDB': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbersDB)],
        },
        fallbacks=[]
    )
    # Обработчик диалога
    convHandlerFindEmailNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailNumbersCommand)],
        states={
            'findEmailNumbers': [MessageHandler(Filters.text & ~Filters.command, findEmailNumbers)],
            'findEmailNumbersDB': [MessageHandler(Filters.text & ~Filters.command, findEmailNumbersDB)],
        },
        fallbacks=[]
    )
    # Обработчик диалога
    convHandlerFindPasswordNumbers = ConversationHandler(
        entry_points=[CommandHandler('verify_password', findPasswordNumbersCommand)],
        states={
            'findPasswordNumbers': [MessageHandler(Filters.text & ~Filters.command, findPasswordNumbers)],
        },
        fallbacks=[]
    )

    # Обработчик диалога
    convHandler_get_apt_list_grep = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list_grep', set_apt_list_grep)],
        states={
            'get_apt_list_grep': [MessageHandler(Filters.text & ~Filters.command, get_apt_list_grep)],
        },
        fallbacks=[]
    )

    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_apt_list", get_apt_list))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmailNumbers)
    dp.add_handler(convHandlerFindPasswordNumbers)
    dp.add_handler(convHandler_get_apt_list_grep)

    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
