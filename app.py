import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# Заголовок приложения
st.title("Финансовые инструменты")

# Функция для получения данных ставки ЦБ РФ
def get_exchange_rates():
    moex_url_cbrf = 'https://iss.moex.com//iss/statistics/engines/currency/markets/selt/rates.json'
    
    try:
        response = requests.get(moex_url_cbrf)
        if response.status_code == 200:
            result = response.json()
            col_names = result['cbrf']['columns']
            df = pd.DataFrame(result['cbrf']['data'], columns=col_names)
            return df
        else:
            st.error(f'Ошибка при получении данных. Код состояния: {response.status_code}')
    except Exception as e:
        st.error(f'Произошла ошибка при запросе данных: {e}')

# Функция для получения данных кривых свопов
def get_swap_curves():
    moex_url = 'https://iss.moex.com//iss/sdfi/curves/securities.json'
    
    try:
        response = requests.get(moex_url)
        if response.status_code == 200:
            result = response.json()
            col_names = result['curves']['columns']
            df = pd.DataFrame(result['curves']['data'], columns=col_names)
            return df
        else:
            st.error(f'Ошибка при получении данных. Код состояния: {response.status_code}')
    except Exception as e:
        st.error(f'Произошла ошибка при запросов данных: {e}')

# Функция для получения данных MOEX
def get_moex_data():
    moex_url = 'https://iss.moex.com/iss/engines/stock/markets/index/securities/imoex.json'
    
    try:
        response = requests.get(moex_url)
        if response.status_code == 200:
            result = response.json()
            col_names = result['marketdata']['columns']
            df = pd.DataFrame(result['marketdata']['data'], columns=col_names)
            return df
        else:
            st.error(f'Ошибка при получении данных. Код состояния: {response.status_code}')
    except Exception as e:
        st.error(f'Произошла ошибка при запросах данных: {e}')

# Объединенная функция для получения всех данных
def get_all_data():
    # Получаем данные по валютам
    exchange_rates = get_exchange_rates()
    # Получаем данные по кривым свопов
    swap_curves = get_swap_curves()
    # Получаем данные по MOEX
    moex_data = get_moex_data()
    
    # Объединяем данные в единый DataFrame
    final_data = pd.concat([exchange_rates, swap_curves, moex_data], axis=1)
    
    # Форматируем и добавляем нужные колонки
    final_data = final_data.reset_index(drop=False)
    final_data = final_data[['CBRF_USD_LAST', 'swap_rate', 'CURRENTVALUE']]
    final_data['USD_CHANGE'] = final_data['CBRF_USD_LASTCHANGEPRCNT']
    final_data['EUR_CHANGE'] = final_data['CBRF_EUR_LASTCHANGEPRCNT']
    final_data['MOEX_CHANGE'] = final_data['LASTCHANGE']
    final_data['USD_DATE'] = pd.to_datetime(final_data['CBRF_USD_TRADEDATE']).dt.date
    final_data['EUR_DATE'] = pd.to_datetime(final_data['CBRF_EUR_TRADEDATE']).dt.date
    final_data['MOEX_DATE'] = final_data['TRADEDATE']
    
    # Разделяем данные на четыре колонки
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.subheader("Доллар США")
        st.write(f"Курс: ${final_data['CBRF_USD_LAST'].round(2)}")
        change_color = "green" if final_data['USD_CHANGE'] > 0 else "red"
        st.markdown(f"<p style='color:{change_color}; font-size:20px;'>Изменение: {final_data['USD_CHANGE']:.2f}%</p>", unsafe_allow_html=True)
        st.write(f"Дата обновления: {final_data['USD_DATE']} (USD)")
    
    with col2:
        st.subheader("Евро")
        st.write(f"Курс: €{final_data['CBRF_EUR_LAST'].round(2)}")
        change_color = "green" if final_data['EUR_CHANGE'] > 0 else "red"
        st.markdown(f"<p style='color:{change_color}; font-size:20px;'>Изменение: {final_data['EUR_CHANGE']:.2f}%</p>", unsafe_allow_html=True)
        st.write(f"Дата обновления: {final_data['EUR_DATE']} (EUR)")
    
    with col3:
        st.subheader("RGBI")
        st.write(f"Курс: {final_data['CURRENTVALUE'].round(2)}")
        change_color = "green" if final_data['MOEX_CHANGE'] > 0 else "red"
        st.markdown(f"<p style='color:{change_color}; font-size:20px;'>Изменение: {final_data['MOEX_CHANGE']:.2f}%</p>", unsafe_allow_html=True)
        st.write(f"Дата обновления: {final_data['MOEX_DATE']} (RGBI)")
    
    with col4:
        st.subheader("IMOEX")
        st.write(f"Курс: {final_data['CURRENTVALUE'].round(2)}")
        change_color = "green" if final_data['MOEX_CHANGE'] > 0 else "red"
        st.markdown(f"<p style='color:{change_color}; font-size:20px;'>Изменение: {final_data['MOEX_CHANGE']:.2f}%</p>", unsafe_allow_html=True)
        st.write(f"Дата обновления: {final_data['MOEX_DATE']} (IMOEX)")

# Блок с графиками кривых свопов
st.header("Графики кривых свопов")

# Автоматический запрос данных
curves_data = get_swap_curves()

if curves_data is not None:
    # Убедимся, что столбец 'swap_curve' существует
    if 'swap_curve' in curves_data.columns:
        swap_curve_filter = st.selectbox('Выберите кривую:', options=curves_data['swap_curve'].unique())
        filtered_data = curves_data.query(f"swap_curve == '{swap_curve_filter}'")
        
        # Получение даты выгрузки
        trade_date_str = filtered_data['tradedate'].values[0]
        trade_date = datetime.strptime(trade_date_str, '%Y-%m-%d').strftime('%d.%m.%Y')  # Преобразуем формат даты
        
        # Выводим дату выгрузки
        st.write(f"Дата выгрузки: {trade_date}")
        
        # Строим график
        fig = px.line(filtered_data, x='tenor', y='swap_rate', title=f"Кривая '{swap_curve_filter}'",
                     labels={'tenor': 'Срок', 'swap_rate': 'Ставка'},
                     template='plotly_dark')
        
        # Отображаем график
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Столбец 'swap_curve' отсутствует в данных.")
else:
    st.warning("Не удалось получить данные.")

# Блок с таблицей MOEX
st.header("Таблица MOEX")

# Отображение таблицы
moex_table = final_data
st.dataframe(moex_table)

# Завершающая часть кода
if final_data is not None:
    st.text(f"Данные MOEX успешно получены и отображены.")
else:
    st.warning("Не удалось получить данные MOEX.")

# Заключение
Этот код представляет собой упрощенную версию работы с финансовыми инструментами, включая курсы валют, кривые свопов и данные MOEX. Он обеспечивает простоту взаимодействия с различными источниками данных и улучшает визуализацию финансовых показателей.
