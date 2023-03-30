import numpy as np
#import pandas as pd
import streamlit as st
import constants as const
from vectorize_cluster import vectorize_cluster
import suspicious_strings_io
from preprocessing import preprocessing
#import matplotlib.pyplot as plt
import clustered_analyzer as ca
import streamlit_utilities as su
import classification_model as cm
import jsonpickle


def main():
    #if "pipeline_step_number" in st.session_state:
    #    print(st.session_state["pipeline_step_number"])
    data_url = st.text_input("URL csv-файла с данными", const.default_data_url, on_change=lambda: su.set_pipeline_step(0))


    column1, column2 = st.columns(2)
    with column2.form('use_existing_model'):
        "Предсказать с использованием существующей модели"
        file_name = st.text_input("Имя файла с моделью (.cbm)", const.default_model_filename)
        target_file_name = st.text_input("Имя файла, куда нужно сохранить результат (в формате .csv)", const.default_target_filename)
        submitted = st.form_submit_button("Submit")
        if submitted:
            su.set_pipeline_step(0)
            predict(data_url, file_name, target_file_name)
    su.session_state_button(column1, "Загрузить данные для обучения модели", 1)

    #preprocessed_data_expander = st.expander("Показать загруженные данные")
    #preprocessed_data_expander.dataframe(data)


    suspicious_strings_list = suspicious_strings_io.load()
    suspicious_strings = np.asarray(suspicious_strings_list)

    suspicious_expander = st.expander("Редактор подозрительных строк")

    suspicious_expander.dataframe(suspicious_strings)

    with suspicious_expander.form("suspicious_strings_add_form", clear_on_submit=True):
        "Добавить подозрительную строку"
        suspicious_string = st.text_input("Подозрительная строка")
        submitted = st.form_submit_button("Submit")
        if submitted and suspicious_string not in suspicious_strings_list:
            suspicious_strings_list.append(suspicious_string)
            #suspicious_strings = np.asarray(suspicious_strings_list)
            suspicious_strings_io.save(suspicious_strings_list)
            su.set_pipeline_step(1)
            st.experimental_rerun()

    with suspicious_expander.form("suspicious_strings_delete_form", clear_on_submit=True):
        "Удалить подозрительную строку"
        suspicious_string = st.selectbox("Подозрительная строка", suspicious_strings)
        submitted = st.form_submit_button("Submit")
        if submitted:
            suspicious_strings_list.remove(suspicious_string)
            #suspicious_strings = np.asarray(suspicious_strings_list)
            suspicious_strings_io.save(suspicious_strings_list)
            su.set_pipeline_step(1)
            st.experimental_rerun()

    # if 'preprocessing_done' not in st.session_state:
    #     st.session_state['preprocessing_done'] = False
    #
    # if st.button("Начать предобработку"):
    #     st.session_state['preprocessing_done'] = True
    #
    # if not st.session_state['preprocessing_done']:
    #     return
    #
    # st.session_state['preprocessing_done'] = True
    su.session_state_button(st, "Начать предобработку", 2)


    data = preprocessing(data_url, suspicious_strings_list)

    preprocessed_data_expander = st.expander("Показать предобработанные данные")
    preprocessed_data_expander.dataframe(data)

    hyperparameters_expander = st.expander("Редактор гиперпараметров")

    hyperparameters_expander.header("Гиперпараметры векторизации")
    hyperparameters_expander.write("Размер n-граммы")
    col1, col2 = hyperparameters_expander.columns(2)

    #col1.header("От")
    ngram_lower = col1.number_input("От", value=const.ngram_lower, min_value=1, on_change=lambda: su.set_pipeline_step(2))

    #col2.header("До")
    ngram_upper = col2.number_input("До", value=const.ngram_upper, min_value=1, on_change=lambda: su.set_pipeline_step(2))

    #"Максимальное количество новых столбцов"
    max_features = hyperparameters_expander.number_input("Максимальное количество новых столбцов", value=const.max_features, min_value=0, on_change=lambda: su.set_pipeline_step(2))

    hyperparameters_expander.header("Гиперпараметры кластеризации")
    #"Eps"
    eps = hyperparameters_expander.number_input("Eps", value=const.eps, min_value=0.0, on_change=lambda: su.set_pipeline_step(2))
    #"Минимальный размер кластера"
    min_samples = hyperparameters_expander.number_input("Минимальный размер кластера", value=const.min_samples, min_value=1, on_change=lambda: su.set_pipeline_step(2))

    #if not st.button("Начать кластеризацию"):
    #    return

    # if 'clustering_done' not in st.session_state:
    #     st.session_state['clustering_done'] = False
    #
    # if st.button("Начать кластеризацию"):
    #     st.session_state['clustering_done'] = True
    #
    # if not st.session_state['clustering_done']:
    #     return
    #
    # st.session_state['clustering_done'] = True
    su.session_state_button(st, "Начать векторизацию и кластеризацию", 3)


    clustered, clustered_vectorized, hyperparameters = vectorize_cluster(data, round(ngram_lower), round(ngram_upper), round(max_features), eps, round(min_samples))
    #ca.hist_clusters_of_column_values(clustered, 'suspicious_meta1', 1)
    #clustered['suspicious_meta1'].hist()
    # fig = plt.figure(figsize=(10, 4))
    # plt.hist(clustered['suspicious_meta1'])
    # st.pyplot(fig)

    unclassified_count, unclassified_ratio, cluster_count = ca.get_clustering_stats(clustered)

    clustered_data_metrics = st.expander("Посмотреть метрики кластеризации")
    clustered_data_metrics.write(f"Количество некластеризованных элементов: {unclassified_count}")
    clustered_data_metrics.write(f"Доля некластеризованных элементов: {unclassified_ratio}")
    clustered_data_metrics.write(f"Количество кластеров: {cluster_count}")
    clustered_data_metrics.write("Распределение элементов по кластерам:")
    ca.column_hist(clustered_data_metrics, clustered['clustering_result'])
    #ca.cluster_distribution_hist(clustered_data_metrics, clustered)

    
    clustered_data_expander = st.expander("Показать кластеризованные данные")
    clustered_data_expander.dataframe(clustered)
    clustered_data_expander.write("Столбцы, соответствуюцие n-граммам векторизации, не показываются, так как иначе отображение рендерится очень долго.")

    column_cluster_visualizer = st.expander("Гистограмма соответствия значений столбцов кластерам")
    with column_cluster_visualizer.form('column_cluster_visualizer_form'):
        column_name = st.selectbox("Столбец", clustered_vectorized.columns, index=list(clustered_vectorized.columns).index("suspicious_meta1"))
        value = st.text_input("Значение", value=1)
        submitted = st.form_submit_button("Submit")
        if submitted:
            ca.hist_clusters_of_column_values(st, clustered_vectorized, column_name, value)

    # if 'training_done' not in st.session_state:
    #     st.session_state['training_done'] = False
    #
    # if st.button("Начать обучение модели"):
    #     st.session_state['training_done'] = True
    #
    # if not st.session_state['training_done']:
    #     return
    #
    # st.session_state['training_done'] = True
    su.session_state_button(st, "Начать обучение модели", 4)


    if const.train_on_subset:
        st.write(f"Для демонстрации обучение происходит на подмножестве датасета из {const.train_subset_size} строк.")

    cat, metrics_tuple = cm.train_test(clustered_vectorized)

    training_metrics = st.expander("Показать метрики модели")
    training_metrics.write(f"Accuracy: {metrics_tuple[0]}")
    training_metrics.write(f"Precision (average='macro'): {metrics_tuple[2]}")
    training_metrics.write(f"Recall (average='macro'): {metrics_tuple[1]}")

    with st.form('save_model_form'):
        "Сохранить модель"
        file_name = st.text_input("Имя файла", const.default_model_filename).removesuffix('.cbm')
        submitted = st.form_submit_button("Submit")
        if submitted:
            cm.save_model(cat, file_name, hyperparameters, suspicious_strings_list)
            st.write(f"Мсдель сохранена в файл {file_name}.cbm")

    #if st.button("Сохранить модель в файл"):
    #    cm.save_model(cat)
    #    st.write("Мсдель сохранена в файл saved_cat_model.cbm")


def predict(data_url, file_name, target_file_name):
    file_name = file_name.removesuffix('.cbm')
    target_file_name = target_file_name.removesuffix('.csv')
    with open(file_name + const.hyperparameters_suffix, 'r') as file:
        json_string = file.read()
    hyperparameters = jsonpickle.decode(json_string)
    data = preprocessing(data_url, hyperparameters.suspicious_strings)
    _, clustered_vectorized, _ = vectorize_cluster(data, hyperparameters.ngram_min, hyperparameters.ngram_max,
                                                   hyperparameters.max_features, hyperparameters.eps, hyperparameters.min_samples,
                                                   vocabulary=hyperparameters.vocabulary)
    data_with_prediction = cm.predict_by_filename(file_name, clustered_vectorized, data)
    target_file_name_csv = target_file_name + ".csv"
    data_with_prediction.to_csv(target_file_name_csv)
    st.write("Данные со столбцом предсказания сохранены в " + target_file_name_csv)


try:
    main()
except su.StreamlitEndRunException:
    pass
