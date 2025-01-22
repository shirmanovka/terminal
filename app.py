import requests
import pandas as pd
from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

# Ваш токен и ID канала
TOKEN = '8128261245:AAGDpEBMeFVsS9MaqoP4HVZEjfwMNzhVX5Q'
CHANNEL_ID = '@dcmterminal'  # Убедитесь, что ваш бот является администратором канала

# Заголовки для запроса
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Функция для скачивания файла и чтения данных
def download_data():
    url = 'https://web.moex.com/moex-web-icdb-api/api/v1/export/listing-applications/xlsx'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        with open('listing_applications.xlsx', 'wb') as f:
            f.write(response.content)
        return pd.read_excel('listing_applications.xlsx')
    else:
        return None

# Функция для отправки таблицы в канал
async def send_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    df = download_data()
    if df is not None:
        columns_to_keep = [
            'Наименование эмитента',
            'ИНН эмитента',
            'Категория(тип) ценной бумаги',
            'Идентификатор выпуска*',
            'Уровень листинга',
            'Дата получения заявления',
            'Дата раскрытия информации'
        ]
        df = df[columns_to_keep]
        df['Категория(тип) ценной бумаги'] = df['Категория(тип) ценной бумаги'].str.replace(' ', '\n')
        
        abbreviation = {
            'Общество с ограниченной ответственностью': 'OOO',
            'Публичное акционерное общество': 'ПАO',
            'Акционерное общество': 'AO'
        }

        df['Наименование эмитента'] = df['Наименование эмитента'].replace(abbreviation)
        
        df_to_send = df.tail(10)
        
        # Создаем CSV файл для отправки
        csv_file = 'latest_listing_applications.csv'
        df_to_send.to_csv(csv_file, index=False)

        with open(csv_file, 'rb') as f:
            await context.bot.send_document(chat_id=CHANNEL_ID, document=f, filename=csv_file)

        os.remove(csv_file)  # Удаляем файл после отправки
    else:
        await context.bot.send_message(chat_id=CHANNEL_ID, text="Ошибка при скачивании данных.")

# Настройка бота
application = ApplicationBuilder().token(TOKEN).build()

# Команда для запуска отправки данных в канал
application.add_handler(CommandHandler("send_data", send_to_channel))

# Запуск бота
application.run_polling()
