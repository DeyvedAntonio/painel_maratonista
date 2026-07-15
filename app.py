import streamlit as st


def main():
    st.set_page_config(
        page_title='Painel Maratonista',
        page_icon=':film_strip:',
        layout='wide',
    )
    st.title(':film_strip: Painel Maratonista')
    st.title('Bem-vindo ao seu painel de controle de produções assistidas!')

    with st.form(key='cadastro_midia_form'):
        st.subheader('Cadastrar nova produção :movie_camera:')

        name = st.text_input('Nome da série/filme:')
        category = st.selectbox(
            label='Categoria',
            options=['Ação', 'Aventura', 'Comédia', 'Drama']
        )

        star_review = range(1, 6)
        reviews = st.select_slider(
            ':material/stars_2: Nota pessoal',
            options=star_review,
        )

        duration = st.number_input('Duração (min)', min_value=0, step=1)

        # O botão de envio do formulário
        submit_button = st.form_submit_button(label='Registrar')

    # 3. Processando o clique do botão fora do form
    if submit_button:
        if name:
            dados = {
                'name': name,
                'category': category,
                'reviews': reviews,
                'duration': duration,
            }
            st.session_state['dados'] = dados

            st.success(
                f'Registrado com sucesso: Você assistiu **{name}** ({category}), deu nota {reviews} e gastou {duration} minutos.'  # NOQA: E501
            )
        else:
            st.error(
                "Por favor, insira o nome da série ou filme antes de registrar."  # NOQA: E501
            )


if __name__ == '__main__':
    main()
