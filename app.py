import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Заголовок приложения
st.title("Фильтр данных по погашению")

    # Чтение данных из Excel
df = pd.read_excel('Карта рынка fix.xlsx', skiprows=1)

    # Преобразование колонки 'Погашение' в формат datetime
df['Погашение'] = pd.to_datetime(df['Погашение'], format='%d-%m-%Y', errors='coerce')

    # Выбор месяца и года для фильтрации
month_to_filter = st.selectbox("Выберите месяц для фильтрации", options=available_months)
year_to_filter = st.selectbox("Выберите год для фильтрации", options=available_years)

 # Проверка, какие месяцы и годы доступны для фильтрации
available_months = df['Погашение'].dt.month.unique()
available_years = df['Погашение'].dt.year.unique()

 
    # Фильтрация по месяцу и году
filtered_df = df[(df['Погашение'].dt.month == month_to_filter) & (df['Погашение'].dt.year == year_to_filter)]

    # Вывод отфильтрованных данных
st.write("Отфильтрованные данные:")
st.dataframe(filtered_df)

    # Визуализация данных (если требуется)
if not filtered_df.empty:
    plt.figure(figsize=(10, 5))
    plt.plot(filtered_df['Погашение'], filtered_df['Объем, млн'], marker='o')  # Замените 'Некоторый_столбец' на нужный вам столбец
    plt.title('График по отфильтрованным данным')
    plt.xlabel('Дата погашения')
    plt.ylabel('Объем, млн')
    st.pyplot(plt)
