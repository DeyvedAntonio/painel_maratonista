import pandas as pd
import streamlit as st
from database import update, delete, load_all, get_dataframe, get_stats, get_badges, check_and_award_badges, get_all_badge_definitions
from datetime import date
import io


# Obter perfil ativo da sessão
active_profile_id = st.session_state.get('active_profile_id', 1)
active_profile_name = st.session_state.get('active_profile_name', 'Principal')

st.subheader(f'📊 Dashboard Analítico — {active_profile_name}')

# Carregar dados do banco (mais atualizado que session_state)
df = get_dataframe(active_profile_id)
stats = get_stats(active_profile_id)

if len(df) > 0:
    # ===== MÉTRICAS PRINCIPAIS =====
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Total de Produções', stats['total'], border=True)
    col2.metric('Tempo Total', f"{stats['total_duration']} min", border=True)
    col3.metric('Média de Avaliação', f"{stats['avg_rating']}/5", border=True)
    col4.metric('Tipos', f"{len(stats['by_type'])} categorias", border=True)

    st.divider()

    # ===== GRÁFICOS =====
    tab1, tab2, tab3, tab4 = st.tabs(['📈 Por Categoria', '🎬 Por Tipo', '📅 Timeline', '🏆 Rankings'])

    with tab1:
        if stats['by_category']:
            cat_df = pd.DataFrame(stats['by_category'])
            st.bar_chart(cat_df.set_index('category')['count'], x_label='Categoria', y_label='Quantidade')
            st.caption('Quantidade de produções por categoria')

    with tab2:
        if stats['by_type']:
            type_df = pd.DataFrame(stats['by_type'])
            col_a, col_b = st.columns(2)
            with col_a:
                st.bar_chart(type_df.set_index('type')['count'], x_label='Tipo', y_label='Quantidade')
            with col_b:
                st.bar_chart(type_df.set_index('type')['total_min'], x_label='Tipo', y_label='Minutos Totais')

    with tab3:
        if stats['timeline']:
            tl_df = pd.DataFrame(stats['timeline'])
            tl_df['mes'] = pd.to_datetime(tl_df['mes']).dt.strftime('%m/%Y')
            st.line_chart(tl_df.set_index('mes')['count'], x_label='Mês', y_label='Produções Assistidas')
            st.caption('Produções assistidas por mês (últimos 12 meses)')

    with tab4:
        col_top1, col_top2 = st.columns(2)
        with col_top1:
            st.write('**⏱️ Top 5 Mais Longas**')
            if stats['top_longest']:
                top_long = pd.DataFrame(stats['top_longest'])
                st.dataframe(top_long[['name', 'type', 'category', 'duration']].rename(columns={
                    'name': 'Nome', 'type': 'Tipo', 'category': 'Categoria', 'duration': 'Minutos'
                }), hide_index=True, use_container_width=True)
        with col_top2:
            st.write('**⭐ Top 5 Melhor Avaliadas**')
            if stats['top_rated']:
                top_rate = pd.DataFrame(stats['top_rated'])
                st.dataframe(top_rate[['name', 'type', 'category', 'reviews']].rename(columns={
                    'name': 'Nome', 'type': 'Tipo', 'category': 'Categoria', 'reviews': 'Nota'
                }), hide_index=True, use_container_width=True)

    st.divider()

    # ===== FILTROS =====
    st.subheader('🔍 Filtros e Tabela de Produções')
    with st.expander('Filtros', expanded=True):
        fcol1, fcol2, fcol3, fcol4 = st.columns(4)
        with fcol1:
            type_filter = st.multiselect('Tipo', options=df['type'].unique(), default=df['type'].unique())
        with fcol2:
            cat_filter = st.multiselect('Categoria', options=sorted(df['category'].unique()), default=sorted(df['category'].unique()))
        with fcol3:
            status_filter = st.multiselect('Status', options=sorted(df['status'].unique()), default=sorted(df['status'].unique()))
        with fcol4:
            rating_filter = st.slider('Avaliação mínima', 1, 5, 1)

    # Aplicar filtros
    filtered = df[
        (df['type'].isin(type_filter)) &
        (df['category'].isin(cat_filter)) &
        (df['status'].isin(status_filter)) &
        (df['reviews'] >= rating_filter)
    ]

    st.caption(f'{len(filtered)} de {len(df)} produções exibidas')

    # ===== EDITOR DE DADOS =====
    if len(filtered) > 0:
        display_cols = ['id', 'name', 'type', 'category', 'reviews', 'duration', 'seasons', 'episodes_watched', 'total_episodes', 'status', 'watched_at']
        df_display = filtered[display_cols].copy()
        df_display.columns = ['ID', 'Nome', 'Tipo', 'Categoria', 'Avaliação', 'Duração (min)', 'Temporadas', 'Eps. Assistidos', 'Total Eps.', 'Status', 'Data']
        # DateColumn exige dtype datetime; o SQLite retorna watched_at como string
        df_display['Data'] = pd.to_datetime(df_display['Data'])

        column_config = {
            'ID': st.column_config.NumberColumn(disabled=True, width='small'),
            'Nome': st.column_config.TextColumn(width='large', required=True),
            'Tipo': st.column_config.SelectboxColumn(options=['Filme', 'Série'], width='small', required=True),
            'Categoria': st.column_config.SelectboxColumn(options=sorted(df['category'].unique()), width='medium', required=True),
            'Avaliação': st.column_config.NumberColumn(min_value=1, max_value=5, step=1, width='small', required=True),
            'Duração (min)': st.column_config.NumberColumn(min_value=1, step=1, width='small', required=True),
            'Temporadas': st.column_config.NumberColumn(min_value=1, max_value=50, step=1, width='small'),
            'Eps. Assistidos': st.column_config.NumberColumn(min_value=0, step=1, width='small'),
            'Total Eps.': st.column_config.NumberColumn(min_value=1, step=1, width='small'),
            'Status': st.column_config.SelectboxColumn(options=['Assistido', 'Assistindo', 'Pretendo Assistir', 'Abandonado'], width='medium', required=True),
            'Data': st.column_config.DateColumn(width='small', required=True),
        }

        edited_df = st.data_editor(
            df_display,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            num_rows='fixed',
            key='editor_producoes',
        )

        # Detectar e salvar mudanças
        if not edited_df.equals(df_display):
            changes = 0
            for _, row in edited_df.iterrows():
                original = df_display[df_display['ID'] == row['ID']].iloc[0]
                if not row.equals(original):
                    update(
                        int(row['ID']),
                        {
                            'name': row['Nome'],
                            'type': row['Tipo'],
                            'category': row['Categoria'],
                            'reviews': int(row['Avaliação']),
                            'duration': int(row['Duração (min)']),
                            'seasons': int(row['Temporadas']),
                            'episodes_watched': int(row['Eps. Assistidos']),
                            'total_episodes': int(row['Total Eps.']),
                            'status': row['Status'],
                            'watched_at': row['Data'] if isinstance(row['Data'], str) else pd.Timestamp(row['Data']).strftime('%Y-%m-%d'),
                        },
                        active_profile_id,
                    )
                    changes += 1
            if changes:
                st.session_state.historico = load_all(active_profile_id)
                st.success(f'{changes} alteração(ões) salva(s)!')
                st.rerun()

    # ===== EXCLUSÃO =====
    st.divider()
    st.subheader('🗑️ Excluir Produção')
    col_del1, col_del2, col_del3 = st.columns([3, 1, 1])
    with col_del1:
        id_to_delete = st.selectbox(
            'Selecione para excluir',
            options=df['id'].tolist(),
            format_func=lambda x: f"ID {x} | {df[df['id']==x]['name'].values[0]} ({df[df['id']==x]['type'].values[0]})",
            key='delete_select',
        )
    with col_del2:
        confirm = st.checkbox('Confirmo exclusão', key='delete_confirm')
    with col_del3:
        if st.button('Excluir Definitivamente', type='primary', use_container_width=True, disabled=not confirm):
            if delete(id_to_delete, active_profile_id):
                st.session_state.historico = load_all(active_profile_id)
                st.success(f'Produção ID {id_to_delete} excluída!')
                st.rerun()
            else:
                st.error('Erro ao excluir.')

    # ===== EXPORTAÇÃO =====
    st.divider()
    st.subheader('📤 Exportar Dados')
    exp_col1, exp_col2, exp_col3 = st.columns(3)
    with exp_col1:
        csv = filtered.to_csv(index=False).encode('utf-8')
        st.download_button('📥 CSV', csv, f'painel_maratonista_{date.today()}.csv', 'text/csv', use_container_width=True)
    with exp_col2:
        json_str = filtered.to_json(orient='records', force_ascii=False, indent=2)
        st.download_button('📥 JSON', json_str, f'painel_maratonista_{date.today()}.json', 'application/json', use_container_width=True)
    with exp_col3:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            filtered.to_excel(writer, index=False, sheet_name='Producoes')
        st.download_button('📥 Excel', excel_buffer.getvalue(), f'painel_maratonista_{date.today()}.xlsx',
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)

    # ===== BADGES / CONQUISTAS =====
    st.divider()
    st.subheader('🏅 Conquistas (Badges)')
    
    # Verificar e conceder badges automaticamente
    new_badges = check_and_award_badges(active_profile_id)
    if new_badges:
        for b in new_badges:
            st.balloons()
            st.success(f'🎉 Nova conquista: {b["emoji"]} **{b["name"]}** — {b["desc"]}')
    
    earned_badges = get_badges(active_profile_id)
    all_badges = get_all_badge_definitions()
    
    if earned_badges:
        st.write('**Conquistadas:**')
        cols = st.columns(min(5, len(earned_badges)))
        for i, badge in enumerate(earned_badges):
            with cols[i % 5]:
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; border-radius: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; margin: 5px;">
                    <div style="font-size: 3rem;">{badge['badge_emoji']}</div>
                    <div style="font-weight: bold;">{badge['badge_name']}</div>
                    <div style="font-size: 0.8rem; opacity: 0.9;">{all_badges.get(badge['badge_key'], {}).get('desc', '')}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info('Nenhuma conquista ainda. Continue assistindo e cadastrando para desbloquear badges!')
    
    # Mostrar progresso para próximas badges
    with st.expander('📋 Ver todas as conquistas e progresso'):
        df = get_dataframe(active_profile_id)
        total_prods = len(df)
        total_min = int(df['duration'].sum()) if len(df) > 0 else 0
        movies = df[df['type'] == 'Filme'] if len(df) > 0 else pd.DataFrame()
        series = df[df['type'] == 'Série'] if len(df) > 0 else pd.DataFrame()
        completed_series = series[series['episodes_watched'] >= series['total_episodes']] if len(series) > 0 else pd.DataFrame()
        total_eps = int(series['episodes_watched'].sum()) if len(series) > 0 else 0
        unique_cats = df['category'].nunique() if len(df) > 0 else 0
        perfect_scores = len(df[df['reviews'] == 5]) if len(df) > 0 else 0
        earned_keys = {b['badge_key'] for b in earned_badges}
        
        progress_data = [
            ("first_steps", f"1 produção ({total_prods}/1)", total_prods >= 1),
            ("marathoner", f"10 produções ({total_prods}/10)", total_prods >= 10),
            ("critic", f"5 notas máximas ({perfect_scores}/5)", perfect_scores >= 5),
            ("binge_watcher", f"50 episódios ({total_eps}/50)", total_eps >= 50),
            ("film_buff", f"20 filmes ({len(movies)}/20)", len(movies) >= 20),
            ("series_addict", f"10 séries ({len(series)}/10)", len(series) >= 10),
            ("genre_explorer", f"5 categorias ({unique_cats}/5)", unique_cats >= 5),
            ("time_lord", f"5000 min ({total_min}/5000)", total_min >= 5000),
            ("completionist", f"10 séries completas ({len(completed_series)}/10)", len(completed_series) >= 10),
        ]
        
        for key, progress, done in progress_data:
            badge = all_badges[key]
            status = "✅" if done else "🔒"
            if key in earned_keys:
                status = "🏆"
            st.write(f"{status} **{badge['emoji']} {badge['name']}** — {badge['desc']}  \n   *{progress}*")

else:
    st.info(
        'Nenhuma produção cadastrada ainda.\n'
        'Vá até a página de **Cadastro** para adicionar seus filmes e séries!'
    )