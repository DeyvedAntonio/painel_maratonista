import streamlit as st


st.subheader('Simulador de Maratona')

with st.form(key='simulador_maratona'):
    st.write('Vamos simular a sua próxima maratona?')
    name = st.text_input('Nome da nova série')
    quantity = st.number_input('Quantidade de episódios')
    avg_duration = st.number_input('Duração média de cada episódio em minutos')
    time = st.number_input(
        'Tempo disponível para assistir por dia',
        step=int(),
        min_value=1,
        max_value=60,
    )
    submit_button = st.form_submit_button(label='Simular')

if submit_button:
    total_duration = quantity * avg_duration
    days = total_duration / time
    st.info(f'Para maratonar {name}, você precisará de um total de \
        {total_duration} minutos. Dedicando {time} minutos por dia \
        você concluirá a série em aproximadamente {days:.0f} dias!')
