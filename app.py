import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Заголовок приложения
st.title("Фильтр данных по погашению")

# Чтение данных из Excel
df = pd.read_excel('Карта рынка fix.xlsx', skiprows=1)

# Преобразование колонки 'Погашение' в формат datetime
df['Погашение'] = pd.to_datetime(df['Погашение'], format='%d-%m-%Y', errors='coerce')

# Очистка и преобразование столбца 'Объем, млн'
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
                  (df['Валюта'].isin(selected_currency))]

# Вывод отфильтрованных данных
st.write("Отфильтрованные данные:")
st.dataframe(filtered_df)

# Визуализация данных (если есть отфильтрованные данные)
if not filtered_df.empty:
    # Создание графика с использованием Plotly
    fig = go.Figure(data=[
        go.Bar(
            x=filtered_df['Погашение'],
            y=filtered_df['Объем, млн'],
            text=filtered_df['Тикер'],  # Подписи для всплывающих подсказок
            hoverinfo='text',  # Показать только текст при наведении
            marker_color='darkred'
        )
    ])

    # Обновление макета графика
    fig.update_layout(
        title='График погашений',
        xaxis_title='Дата погашения',
        yaxis_title='Объем, млн',
        xaxis_tickformat='%Y-%m-%d'
    )

    # Отображение графика в Streamlit
    st.plotly_chart(fig)
else:
    st.write("Нет данных для отображения с выбранными параметрами.")
