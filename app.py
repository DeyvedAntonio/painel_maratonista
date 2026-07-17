import streamlit as st


def home():
    st.set_page_config(
        page_title='Painel Maratonista',
        page_icon=':film_strip:',
        layout='wide',
    )
    st.title(':film_strip: Painel Maratonista')
    st.title('Bem-vindo ao seu painel de controle de produções assistidas!')


if __name__ == '__main__':
    if 'historico' not in st.session_state:
        st.session_state['historico'] = []

    pages = {
        'Home': [
            st.Page(home, title='Home')
        ],
        'Cadastro': [
            st.Page('pages/cadastro.py', title='Cadastro')
        ],
        'Painel': [
            st.Page('pages/painel.py', title='Dashboard', icon="🔥"),
            st.Page('pages/simulador.py', title='Simulador')
        ],
    }
    pg = st.navigation(pages, position='top')
    pg.run()
