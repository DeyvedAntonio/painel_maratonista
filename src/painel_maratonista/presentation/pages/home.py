"""Página Home."""

import streamlit as st
from ..components import render_profile_selector, render_profile_management


def render_home():
    """Renderiza página Home."""
    # Serviços do session_state
    profile_service = st.session_state["profile_service"]

    st.title("Painel do Maratonista de Séries & Filmes! 🚀")
    st.subheader("Bem-vindo ao seu painel de controle de produções!")

    st.markdown("""
    ### 🎯 O que você pode fazer aqui:

    **📝 Cadastro** - Registre filmes e séries com detalhes completos:
    - Tipo (Filme/Série), categorias, temporadas, episódios
    - Status (Assistido, Assistindo, Pretendo, Abandonado)
    - Nota pessoal, data de visualização
    - Busca automática no TMDb (preenche tudo sozinho!)

    **📊 Dashboard** - Visualize suas estatísticas:
    - Métricas gerais, gráficos por categoria/tipo/timeline
    - Rankings: mais longas, melhor avaliadas
    - Filtros dinâmicos, edição inline, exportação (CSV/JSON/Excel)

    **🏅 Conquistas** - Desbloqueie badges:
    - Primeiros Passos, Maratonista, Crítico, Binge Watcher
    - Cinéfila, Viciado em Séries, Explorador de Gêneros
    - Senhor do Tempo, Completionista

    **⏱️ Simulador** - Planeje sua próxima maratona:
    - Calcule dias necessários baseado no seu tempo livre
    """)

    # Sidebar: seletor + gerenciamento de perfis
    profiles = profile_service.list_profiles()
    active_id = st.session_state["active_profile_id"]

    def on_profile_change(new_id):
        st.session_state["active_profile_id"] = new_id
        st.rerun()

    new_active_id = render_profile_selector(profiles, active_id, on_profile_change)
    render_profile_management(profile_service)

    # Perfil ativo info
    active_profile = next((p for p in profiles if p.id == new_active_id), profiles[0])
    st.info(f"👤 Perfil ativo: **{active_profile.avatar_emoji} {active_profile.name}**")