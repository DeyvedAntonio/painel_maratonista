import pandas as pd
import streamlit as st


st.subheader('📊 Histórico de Produções')

if len(st.session_state.historico) > 0:
    df = pd.DataFrame(st.session_state.historico)

    df_formatado = df.rename(columns={
        'name': 'Nome',
        'category': 'Categoria',
        'reviews': 'Avaliação',
        'duration': 'Duração (min)',
    })

    st.dataframe(df_formatado, use_container_width=True)
else:
    st.info('Nenhuma produção cadastrada ainda.\
        Vá até a página de Cadastro para adicionar \
        seus filmes e séries!')
