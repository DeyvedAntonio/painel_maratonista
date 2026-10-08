import streamlit as st


st.subheader('Simulador de Maratona')

with st.form(key='simulador_maratona'):
    st.write('Vamos simular a sua próxima maratona?')
    name = st.text_input('Nome da nova série')
    quantity = st.number_input('Quantidade de episódios', min_value=1, step=1)
    avg_duration = st.number_input('Duração média de cada episódio em minutos', min_value=1, step=1)
    time = st.number_input(
        'Tempo disponível para assistir por dia (min)',
        step=1,
        min_value=1,
        max_value=720,
    )
    submit_button = st.form_submit_button(label='Simular')

if submit_button:
    total_duration = quantity * avg_duration
    days = total_duration / time
    st.info(f'Para maratonar {name}, você precisará de um total de '
            f'{total_duration} minutos. Dedicando {time} minutos por dia '
            f'você concluirá a série em aproximadamente {days:.0f} dias!')
