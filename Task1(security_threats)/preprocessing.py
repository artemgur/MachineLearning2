import pandas as pd
import constants as const
import streamlit as st


# def nan_drop_rows_or_substitute(data):
#     rows_count = data.shape[0]
#
#     for column_name in data.columns:
#         nan_fraction = data[column_name].isna().sum() / rows_count
#         if nan_fraction > const.drop_nan_threshold:
#             # Mark values as missing
#             data[column_name] = data[column_name].replace({None: 'Missing'})
#         else:
#             # Drop NaN rows
#             data.dropna(subset=(column_name,), inplace=True)
#
#     return data


def nan_substitute(data):
    data = data.replace({None: 'Missing'})
    return data


def create_new_features(data, suspicious_strings):
    # Признак 'http_code_type' будет содержать тип кода состояния (успех — 2xx, перенаправление — 3xx, ...)
    data['http_code_type'] = (data['meta3'].astype(float) // 100).astype(str)

    # Отконвертируем содержимое столбца vector в нижний регистр.
    data['vector'] = data['vector'].str.lower()

    # Создадим отдельные столбцы для подозрительных строк.
    for suspicious_str in suspicious_strings:
        data[suspicious_str] = data['vector'].apply(lambda x: 1 if suspicious_str in x else 0)

    # Создадим новый столбец, в котором будет стоять 1, если meta1 — подозрительный, иначе — 0.
    data['suspicious_meta1'] = data['meta1'].apply(lambda x: 1 if ';' in x else 0)

    return data


@st.experimental_memo
def preprocessing(data_url, suspicious_strings):
    data = pd.read_csv(data_url)

    # Оставляет в данных только поддерживаемые столбцы. Остальные столбцы удаляются
    data = data.loc[:, const.supported_initial_columns]
    data = data.astype(str)

    data = nan_substitute(data)

    data = create_new_features(data, suspicious_strings)

    return data
