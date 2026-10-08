import streamlit as st
from database import insert
from datetime import date
from tmdb import search_tmdb, fetch_metadata, get_tmdb_client


# Obter perfil ativo da sessão
active_profile_id = st.session_state.get('active_profile_id', 1)


# --- UI: Busca TMDb (fora do form para funcionar como autocomplete) ---
st.subheader('🔍 Buscar no TMDb (opcional)')
tmdb_client = get_tmdb_client()

if not tmdb_client.is_configured():
    st.info(
        '💡 Configure a variável de ambiente `TMDB_API_KEY` para habilitar '
        'busca automática e preenchimento de metadados (gênero, duração, sinopse, pôster). '
        'Obtenha sua chave grátis em [themoviedb.org](https://www.themoviedb.org/settings/api).'
    )
else:
    search_query = st.text_input(
        'Digite o nome da série/filme para buscar no TMDb:',
        placeholder='Ex: Breaking Bad, Interestelar, The Office...',
        key='tmdb_search_input',
    )

    if search_query:
        with st.spinner('Buscando...'):
            results = search_tmdb(search_query)

        if results:
            selected = st.selectbox(
                'Resultados:',
                options=results,
                format_func=lambda x: x['display'],
                key='tmdb_select_result',
            )

            if selected and st.button('✨ Preencher formulário com dados do TMDb', use_container_width=True):
                with st.spinner('Carregando detalhes...'):
                    meta = fetch_metadata(selected['tmdb_id'], selected['media_type'])

                if meta:
                    # Guardar no session_state para preencher o form
                    for k, v in meta.items():
                        st.session_state[f'tmdb_{k}'] = v
                    st.session_state['tmdb_filled'] = True
                    st.success('Dados carregados! Verifique e ajuste abaixo.')
                    st.rerun()
                else:
                    st.error('Erro ao buscar detalhes completos.')
        else:
            st.caption('Nenhum resultado encontrado.')


st.divider()


# --- FORMULÁRIO PRINCIPAL ---
with st.form(key='cadastro_midia_form'):
    st.subheader(f'Cadastrar nova produção :movie_camera: (Perfil: {st.session_state.get("active_profile_name", "Principal")})')

    # Valores padrão (do TMDb se preenchido, senão vazios)
    default_name = st.session_state.get('tmdb_name', '')
    default_type = st.session_state.get('tmdb_type', 'Série')
    default_category = st.session_state.get('tmdb_category', 'Outro')
    default_duration = st.session_state.get('tmdb_duration', 0)
    default_seasons = st.session_state.get('tmdb_seasons', 1)
    default_total_eps = st.session_state.get('tmdb_total_episodes', 10)
    default_year = st.session_state.get('tmdb_year', '')
    default_overview = st.session_state.get('tmdb_overview', '')
    default_poster = st.session_state.get('tmdb_poster_url', '')
    default_tmdb_rating = st.session_state.get('tmdb_tmdb_rating', 0)

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input('Nome da série/filme:', value=default_name, placeholder='Ex: Breaking Bad')
        type_ = st.selectbox('Tipo', options=['Série', 'Filme'], index=0 if default_type == 'Série' else 1)
    with col2:
        list_category = ['Ação', 'Aventura', 'Comédia', 'Drama', 'Ficção Científica', 'Terror', 'Romance', 'Documentário', 'Animação', 'Outro']
        cat_index = list_category.index(default_category) if default_category in list_category else 9
        category = st.selectbox('Categoria', options=list_category, index=cat_index)
        status = st.selectbox('Status', options=['Assistido', 'Assistindo', 'Pretendo Assistir', 'Abandonado'], index=0)

    # Mostrar pôster e sinopse se vier do TMDb
    if default_poster:
        st.image(default_poster, width=150)
    if default_overview:
        with st.expander('📖 Sinopse (TMDb)'):
            st.write(default_overview)
    if default_tmdb_rating:
        st.caption(f'⭐ Nota TMDb: {default_tmdb_rating:.1f}/10')

    # Campos específicos por tipo
    if type_ == 'Série':
        col3, col4, col5 = st.columns(3)
        with col3:
            seasons = st.number_input('Temporadas', min_value=1, max_value=50, value=default_seasons, step=1)
        with col4:
            total_episodes = st.number_input('Total de episódios', min_value=1, max_value=1000, value=default_total_eps, step=1)
        with col5:
            episodes_watched = st.number_input('Episódios assistidos', min_value=0, max_value=total_episodes, value=0, step=1)
        duration = st.number_input('Duração média por episódio (min)', min_value=1, max_value=300, value=max(1, default_duration), step=1)
    else:  # Filme
        seasons = 1
        total_episodes = 1
        episodes_watched = 1
        duration = st.number_input('Duração (min)', min_value=1, max_value=600, value=max(1, default_duration), step=1)

    star_review = range(1, 6)
    # Sugerir nota baseada no TMDb (convertida 10->5)
    suggested_review = max(1, min(5, round(default_tmdb_rating / 2))) if default_tmdb_rating else 3
    reviews = st.select_slider(
        ':material/stars_2: Nota pessoal',
        options=star_review,
        value=suggested_review,
    )

    watched_at = st.date_input('Data de visualização', value=date.today(), max_value=date.today())

    submit_button = st.form_submit_button(label='Registrar', use_container_width=True)


if submit_button:
    if name:
        dados = {
            'name': name,
            'type': type_,
            'category': category,
            'reviews': reviews,
            'duration': duration,
            'seasons': seasons,
            'episodes_watched': episodes_watched,
            'total_episodes': total_episodes,
            'status': status,
            'watched_at': watched_at.isoformat(),
        }
        novo_id = insert(dados, active_profile_id)
        dados['id'] = novo_id
        st.session_state.historico.insert(0, dados)

        # Limpar dados do TMDb do session_state após sucesso
        for key in list(st.session_state.keys()):
            if key.startswith('tmdb_'):
                del st.session_state[key]

        st.success(
            f'Registrado com sucesso: **{name}** ({type_}, {category}) — '
            f'Nota {reviews}, {duration} min, Status: {status}'
        )
    else:
        st.error('Por favor, insira o nome da série ou filme antes de registrar.')