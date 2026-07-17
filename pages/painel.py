import pandas as pd
import streamlit as st


st.subheader('📊 Histórico de Produções')

if len(st.session_state.historico) > 0:
    total_midias = len(st.session_state.historico)
    df = pd.DataFrame(st.session_state.historico)
    total_duration = df['duration'].sum()
    total_by_category = df['category'].value_counts()
    col1, col2 = st.columns(2)
    col1.metric(
        label='Total de mídias assistidas',
        value=total_midias,
        border=True,
    )
    col2.metric(
        label='Tempo total assistido',
        value=f'{total_duration} min',
        border=True,
    )

    st.bar_chart(
        total_by_category,
        x_label='Categoria',
        y_label='Total',
    )

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
