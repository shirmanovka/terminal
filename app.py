import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Заголовок приложения
st.title("Фильтр данных по погашению")

    # Чтение данных из Excel
df = pd.read_excel('Карта рынка fix.xlsx', skiprows=1)

    # Преобразование колонки 'Погашение' в формат datetime
df['Погашение'] = pd.to_datetime(df['Погашение'], format='%d-%m-%Y', errors='coerce')

df['Объем, млн'] = df['Объем, млн'].astype(str).str.replace("'", "", regex=False)
df['Объем, млн'] = pd.to_numeric(df['Объем, млн'], errors='coerce')


   # Проверка, какие даты доступны для фильтрации
min_date = df['Погашение'].min()
max_date = df['Погашение'].max()

    # Выбор диапазона дат для фильтрации
start_date = st.date_input("Выберите начальную дату", min_value=min_date, max_value=max_date, value=min_date)
end_date = st.date_input("Выберите конечную дату", min_value=min_date, max_value=max_date, value=max_date)

# Фильтрация по валюте
unique_currencies = df['Валюта'].unique()  # Получаем уникальные валюты
selected_currency = st.multiselect("Выберите валюту", unique_currencies)  # Выбор валюты
   
# Фильтрация по диапазону дат
filtered_df = df[(df['Погашение'] >= pd.Timestamp(start_date)) & 
                  (df['Погашение'] <= pd.Timestamp(end_date)) & 
                  (df['Валюта'].isin( selected_currency))]
    # Вывод отфильтрованных данных
st.write("Отфильтрованные данные:")
st.dataframe(filtered_df)

# Визуализация данных (если есть отфильтрованные данные)
if not filtered_df.empty:
    plt.figure(figsize=(10, 5))
    bars = plt.bar(filtered_df['Погашение'], filtered_df['Объем, млн'], color='darkred')
    plt.title('График погашений')
    plt.xlabel('Дата погашения')
    plt.ylabel('Объем, млн')
    plt.xticks(rotation=45)

    # Добавление подписей к столбцам
    for bar, ticker in zip(bars, filtered_df['Тикер']):  # Предполагается, что в DataFrame есть колонка 'Тикер'
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, ticker, ha='center', va='bottom')
    st.pyplot(plt)
else:
    st.write("Нет данных для отображения с выбранными параметрами.")
