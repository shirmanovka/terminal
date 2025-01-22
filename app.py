from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Вставьте ваш токен API
TOKEN = '8128261245:AAGDpEBMeFVsS9MaqoP4HVZEjfwMNzhVX5Q'

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я ваш бот!')

def main():
    # Создаем объект Updater и передаем ему токен
    updater = Updater(TOKEN)

    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Добавляем обработчик команды /start
    dispatcher.add_handler(CommandHandler("start", start))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота, если будет нажата клавиша Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()
