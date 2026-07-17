import streamlit as st


with st.form(key='cadastro_midia_form'):
    st.subheader('Cadastrar nova produção :movie_camera:')
    name = st.text_input('Nome da série/filme:')
    list_category = ['Ação', 'Aventura', 'Comédia', 'Drama']
    category = st.selectbox(
        label='Categoria',
        options=list_category,
    )
    star_review = range(1, 6)
    reviews = st.select_slider(
        ':material/stars_2: Nota pessoal',
        options=star_review,
    )
    duration = st.number_input('Duração (min)', min_value=0, step=1)
    submit_button = st.form_submit_button(label='Registrar')


if submit_button:
    if name:
        dados = {
            'name': name,
            'category': category,
            'reviews': reviews,
            'duration': duration,
        }
        st.session_state.historico.append(dados)
        st.success(
            f'Registrado com sucesso: Você assistiu **{name}** ({category}), deu nota {reviews} e gastou {duration} minutos.'  # NOQA: E501
        )
    else:
        st.error(
            "Por favor, insira o nome da série ou filme antes de registrar."  # NOQA: E501
        )
