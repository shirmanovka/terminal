import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Заголовок приложения
st.title("Фильтр данных по погашению")

df = pd.read_excel('Карта рынка.xlsx', skiprows=1)
df_1 = pd.read_excel('Карта рынка fix.xlsx', skiprows=1)

df_1['Базовая ставка'] ='fix'
df['Базовая ставка'] = 'floater'

#df['Базовая ставка'] = df['Базовая ставка'] + df['Спред, пп']

df['Погашение'] = pd.to_datetime(df['Погашение'], format='%d-%m-%Y', errors='coerce')
df_1['Погашение'] = pd.to_datetime(df_1['Погашение'], format='%d-%m-%Y', errors='coerce')

# Очистка и преобразование столбца 'Объем, млн'
df['Объем, млн'] = df['Объем, млн'].astype(str).str.replace("'", "", regex=False)
df['Объем, млн'] = pd.to_numeric(df['Объем, млн'], errors='coerce')

df_1['Объем, млн'] = df_1['Объем, млн'].astype(str).str.replace("'", "", regex=False)
df_1['Объем, млн'] = pd.to_numeric(df_1['Объем, млн'], errors='coerce')

#Создание малых дата фреймов
df1 = df[['ISIN', 'Тикер', 'Рейтинг', 'Валюта', 'Объем, млн', 
         'Погашение','Опцион', 'Базовая ставка' ]].copy()

df_2 = df_1[['ISIN', 'Тикер', 'Рейтинг', 'Валюта', 'Объем, млн', 
         'Погашение','Опцион','Базовая ставка' ]].copy()


# Заполнить отсутствующие столбцы значением np.nan
df1 = df1.reindex(columns=df_2.columns)
df_2 = df_2.reindex(columns=df1.columns)

# Объединить df1 и df_2
df3 = pd.concat([df1, df_2], ignore_index=True)


# Проверка, какие даты доступны для фильтрации
min_date = df3['Погашение'].min()
max_date = df3['Погашение'].max()

# Выбор диапазона дат для фильтрации
start_date = st.date_input("Выберите начальную дату", min_value=min_date, max_value=max_date, value=min_date)
end_date = st.date_input("Выберите конечную дату", min_value=min_date, max_value=max_date, value=max_date)

# Поле для ввода списка ISIN
isin_input = st.text_area("Введите свои ISIN (по одному на строку):", height=150)

# Преобразуем введенный текст в список ISIN
input_isin_list = [line.strip() for line in isin_input.splitlines() if line.strip()]

# Фильтры для столбцов Тикер и Рейтинг
tickers = df3['Тикер'].unique()
selected_tickers = st.multiselect('Выберите тикер:', tickers)

# Фильтрация по валюте
unique_currencies = df3['Валюта'].unique()  # Получаем уникальные валюты
selected_currency = st.multiselect("Выберите валюту", unique_currencies)  # Выбор валюты


# Фильтрация данных
filtered_df = df3[
    (df3['ISIN'].isin(input_isin_list) | (len(input_isin_list) == 0)) &
    (df3['Тикер'].isin(selected_tickers) | (len(selected_tickers) == 0)) &
    (df3['Погашение'] >= pd.Timestamp(start_date)) &
    (df3['Погашение'] <= pd.Timestamp(end_date)) |
    (df3['Валюта'].isin(selected_currency))
]


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

st.write("Филтрация данных не учитывает наличие оферты у облигации")
else:
    st.write("Нет данных для отображения с выбранными параметрами.")
