import streamlit as st


used_button_session_states = ["Загрузить данные", "Начать предобработку", "Начать векторизацию и кластеризацию", "Начать обучение модели"]


class StreamlitEndRunException(Exception):
    pass

# 0 — до загрузки данных
# 1 — после загрузки данных. Можно настроить подозрительные строки
# 2 — после предобработки данных
# 3 — после векторизации и кластеризации
# 4 — после обучения модели


def session_state_button(streamlit_context, button_text, pipeline_step_number):
    if "pipeline_step_number" not in st.session_state:
        st.session_state["pipeline_step_number"] = 0

    if streamlit_context.button(button_text):
        st.session_state["pipeline_step_number"] = pipeline_step_number

    #if button_text == "Загрузить данные для обучения модели":
    #    print(st.session_state["pipeline_step_number"])
    #    print(st.session_state["pipeline_step_number"] < pipeline_step_number)

    if st.session_state["pipeline_step_number"] < pipeline_step_number:
        raise StreamlitEndRunException()

    #st.session_state["pipeline_step_number"] = pipeline_step_number


# def reset_all_button_session_states():
#     for session_state in used_button_session_states:
#         st.session_state[session_state] = False

def set_pipeline_step(pipeline_step_number):
    #print("Changing pipeline step to " + str(pipeline_step_number))
    st.session_state["pipeline_step_number"] = pipeline_step_number
