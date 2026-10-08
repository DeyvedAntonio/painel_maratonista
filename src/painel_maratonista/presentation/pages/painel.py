"""Página do Dashboard Analítico."""

import streamlit as st
from ..components import (
    render_metric_cards,
    render_charts_tabs,
    render_production_editor,
    render_delete_section,
    render_export_buttons,
    render_badges,
)
from ....domain.enums import MediaCategory, MediaStatus, MediaType
from ....domain.value_objects import Rating, Duration, EpisodeCount, SeasonCount, WatchedDate


def render_painel():
    """Renderiza página do Dashboard."""
    # Serviços do session_state
    production_service = st.session_state["production_service"]
    badge_service = st.session_state["badge_service"]
    active_profile_id = st.session_state["active_profile_id"]
    active_profile_name = st.session_state["active_profile_name"]

    st.subheader(f"📊 Dashboard Analítico — {active_profile_name}")

    # Carregar dados
    productions = production_service.list_productions(active_profile_id)
    stats = production_service.get_stats(active_profile_id)
    badges = badge_service.get_badges(active_profile_id)

    if not productions:
        st.info(
            "Nenhuma produção cadastrada ainda.\n"
            "Vá até a página de **Cadastro** para adicionar seus filmes e séries!"
        )
        return

    # Métricas
    render_metric_cards(stats)

    st.divider()

    # Gráficos
    render_charts_tabs(stats)

    st.divider()

    # Filtros
    st.subheader("🔍 Filtros")
    with st.expander("Filtros", expanded=True):
        fcol1, fcol2, fcol3, fcol4 = st.columns(4)
        with fcol1:
            type_filter = st.multiselect(
                "Tipo",
                options=[MediaType.MOVIE, MediaType.SERIES],
                default=[MediaType.MOVIE, MediaType.SERIES],
                format_func=lambda x: x.value,
            )
        with fcol2:
            categories = sorted(set(p.category.value for p in productions))
            cat_filter = st.multiselect("Categoria", options=categories, default=categories)
        with fcol3:
            statuses = sorted(set(p.status.value for p in productions))
            status_filter = st.multiselect("Status", options=statuses, default=statuses)
        with fcol4:
            rating_filter = st.slider("Avaliação mínima", 1, 5, 1)

    # Aplicar filtros
    filtered = [
        p for p in productions
        if p.type in type_filter
        and p.category.value in cat_filter
        and p.status.value in status_filter
        and p.rating.value >= rating_filter
    ]

    st.caption(f"Exibindo {len(filtered)} de {len(productions)} produções")

    # Editor inline
    def on_save(row):
        prod = next(p for p in productions if p.id == row["ID"])
        prod.name = row["Nome"]
        prod.type = MediaType.from_str(row["Tipo"])
        prod.category = MediaCategory.from_str(row["Categoria"])
        prod.rating = Rating(row["Avaliação"])
        prod.duration = Duration(row["Duração (min)"])
        prod.seasons = SeasonCount(row["Temporadas"])
        prod.episodes_watched = EpisodeCount(row["Eps. Assistidos"])
        prod.total_episodes = EpisodeCount(row["Total Eps."])
        prod.status = MediaStatus.from_str(row["Status"])
        prod.watched_at = WatchedDate.fromisoformat(row["Data"])
        production_service.update_production(prod)

    def on_delete(production_id: int):
        production_service.delete_production(active_profile_id, production_id)

    render_production_editor(filtered, on_save)
    render_delete_section(filtered, on_delete)
    render_export_buttons(filtered, active_profile_name)
    render_badges(badges, stats)