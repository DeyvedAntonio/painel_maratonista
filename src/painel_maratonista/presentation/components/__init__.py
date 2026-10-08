"""Componentes reutilizáveis da UI."""

import streamlit as st
from ....domain.entities import Production, Profile, Badge, Stats
from ....domain.enums import MediaType, MediaStatus, MediaCategory, BadgeKey
from ....domain.value_objects import Rating, Duration, EpisodeCount, SeasonCount, WatchedDate
from datetime import date


def render_profile_selector(profiles: list[Profile], current_id: int, on_change) -> int:
    """Seletor de perfil na sidebar."""
    profile_names = {p.id: f"{p.avatar_emoji} {p.name}" for p in profiles}
    profile_ids = list(profile_names.keys())

    if current_id not in profile_ids:
        current_id = profile_ids[0]

    selected_id = st.sidebar.selectbox(
        "👤 Perfil Ativo",
        options=profile_ids,
        format_func=lambda x: profile_names[x],
        index=profile_ids.index(current_id),
        key="profile_selector",
    )

    if selected_id != current_id:
        on_change(selected_id)

    return selected_id


def render_profile_management(profile_service) -> None:
    """UI para gerenciar perfis (criar/excluir)."""
    with st.sidebar.expander("⚙️ Gerenciar Perfis"):
        with st.form("new_profile_form", clear_on_submit=True):
            new_name = st.text_input("Nome do novo perfil", placeholder="Ex: João, Maria...")
            new_avatar = st.text_input("Emoji", value="👤", max_chars=2)
            if st.form_submit_button("➕ Criar", use_container_width=True):
                if new_name.strip():
                    profile_service.create_profile(new_name.strip(), new_avatar or "👤")
                    st.success(f'Perfil "{new_name}" criado!')
                    st.rerun()
                else:
                    st.error("Nome é obrigatório.")

        profiles = profile_service.list_profiles()
        if len(profiles) > 1:
            st.caption("Excluir perfil (remove todas as produções):")
            del_id = st.selectbox(
                "Perfil para excluir",
                options=[p.id for p in profiles if p.id != 1],
                format_func=lambda x: f"{next(p.avatar_emoji for p in profiles if p.id == x)} {next(p.name for p in profiles if p.id == x)}",
                key="delete_profile_select",
            )
            if st.button("🗑️ Excluir Perfil", type="primary", use_container_width=True):
                try:
                    profile_service.delete_profile(del_id)
                    st.success("Perfil excluído!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))


def render_metric_cards(stats: Stats) -> None:
    """Renderiza cards de métricas principais."""
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Produções", stats.total_productions, border=True)
    col2.metric("Tempo Total", stats.total_watch_time.formatted(), border=True)
    col3.metric("Média de Avaliação", f"{stats.average_rating}/5", border=True)
    col4.metric("Diversidade", f"{stats.unique_categories} categorias", border=True)


def render_charts_tabs(stats: Stats) -> None:
    """Renderiza abas de gráficos."""
    import pandas as pd

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Por Categoria", "🎬 Por Tipo", "📅 Timeline", "🏆 Rankings"])

    with tab1:
        if stats.by_category:
            cat_df = pd.DataFrame(list(stats.by_category.items()), columns=["Categoria", "Quantidade"])
            st.bar_chart(cat_df.set_index("Categoria"), y="Quantidade")
            st.caption("Quantidade de produções por categoria")

    with tab2:
        if stats.by_type:
            type_df = pd.DataFrame(list(stats.by_type.items()), columns=["Tipo", "Quantidade"])
            col_a, col_b = st.columns(2)
            with col_a:
                st.bar_chart(type_df.set_index("Tipo"), y="Quantidade")
                st.caption("Quantidade por tipo")
            with col_b:
                # Precisa de duração por tipo - query separada ou calcular
                st.caption("Minutos por tipo (veja métricas)")

    with tab3:
        if stats.timeline:
            tl_df = pd.DataFrame(stats.timeline)
            tl_df["mes"] = pd.to_datetime(tl_df["mes"]).dt.strftime("%m/%Y")
            st.line_chart(tl_df.set_index("mes")["count"])
            st.caption("Produções assistidas por mês (últimos 12 meses)")

    with tab4:
        col_top1, col_top2 = st.columns(2)
        with col_top1:
            st.write("**⏱️ Top 5 Mais Longas**")
            if stats.top_longest:
                for i, p in enumerate(stats.top_longest, 1):
                    st.write(f"{i}. **{p.name}** ({p.type.value}) — {p.duration.formatted()}")

        with col_top2:
            st.write("**⭐ Top 5 Melhor Avaliadas**")
            if stats.top_rated:
                for i, p in enumerate(stats.top_rated, 1):
                    st.write(f"{i}. **{p.name}** ({p.type.value}) — {Rating(p.rating.value)}")


def render_production_form(
    production: Production | None = None,
    tmdb_data: dict | None = None,
    categories: list[str] | None = None,
) -> dict:
    """Renderiza formulário de cadastro/edição de produção. Retorna dict com dados preenchidos."""
    categories = categories or [c.value for c in MediaCategory]

    # Defaults do TMDb se fornecido
    defaults = tmdb_data or {}

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(
            "Nome da série/filme:",
            value=defaults.get("name", production.name if production else ""),
            placeholder="Ex: Breaking Bad",
        )
        type_ = st.selectbox(
            "Tipo",
            options=[MediaType.SERIES, MediaType.MOVIE],
            index=0 if (defaults.get("type", production.type if production else MediaType.SERIES) == MediaType.SERIES) else 1,
            format_func=lambda x: x.value,
        )
    with col2:
        cat_default = defaults.get("category", production.category if production else MediaCategory.OTHER)
        cat_index = categories.index(cat_default.value) if cat_default.value in categories else len(categories) - 1
        category = st.selectbox("Categoria", options=categories, index=cat_index)

        status_default = defaults.get("status", production.status if production else MediaStatus.WATCHED)
        status = st.selectbox(
            "Status",
            options=[MediaStatus.WATCHED, MediaStatus.WATCHING, MediaStatus.PLAN_TO_WATCH, MediaStatus.DROPPED],
            index=[MediaStatus.WATCHED, MediaStatus.WATCHING, MediaStatus.PLAN_TO_WATCH, MediaStatus.DROPPED].index(status_default),
            format_func=lambda x: x.value,
        )

    # Poster e sinopse do TMDb
    if defaults.get("poster_url"):
        st.image(defaults["poster_url"], width=150)
    if defaults.get("overview"):
        with st.expander("📖 Sinopse (TMDb)"):
            st.write(defaults["overview"])
    if defaults.get("tmdb_rating"):
        st.caption(f"⭐ Nota TMDb: {defaults['tmdb_rating']:.1f}/10")

    # Campos específicos por tipo
    if type_ == MediaType.SERIES:
        col3, col4, col5 = st.columns(3)
        with col3:
            seasons = st.number_input("Temporadas", min_value=1, max_value=50, value=int(defaults.get("seasons", production.seasons if production else SeasonCount(1))), step=1)
        with col4:
            total_episodes = st.number_input("Total de episódios", min_value=1, max_value=1000, value=int(defaults.get("total_episodes", production.total_episodes if production else EpisodeCount(10))), step=1)
        with col5:
            episodes_watched = st.number_input("Episódios assistidos", min_value=0, max_value=total_episodes, value=int(defaults.get("episodes_watched", production.episodes_watched if production else EpisodeCount(0))), step=1)
        duration = st.number_input("Duração média por episódio (min)", min_value=1, max_value=300, value=int(defaults.get("duration", production.duration if production else Duration(45))), step=1)
    else:
        seasons = SeasonCount(1)
        total_episodes = EpisodeCount(1)
        episodes_watched = EpisodeCount(1)
        duration = st.number_input("Duração (min)", min_value=1, max_value=600, value=int(defaults.get("duration", production.duration if production else Duration(120))), step=1)

    # Nota
    suggested_review = int(defaults.get("tmdb_rating", 0) / 2) if defaults.get("tmdb_rating") else (int(production.rating) if production else 3)
    suggested_review = max(1, min(5, suggested_review))
    rating = st.select_slider(
        ":material/stars_2: Nota pessoal",
        options=[1, 2, 3, 4, 5],
        value=suggested_review,
    )

    watched_at = st.date_input(
        "Data de visualização",
        value=defaults.get("watched_at", production.watched_at.value if production else date.today()),
        max_value=date.today(),
    )

    return {
        "name": name,
        "type": type_,
        "category": MediaCategory.from_str(category),
        "rating": Rating(rating),
        "duration": Duration(duration),
        "seasons": SeasonCount(seasons),
        "episodes_watched": EpisodeCount(episodes_watched),
        "total_episodes": EpisodeCount(total_episodes),
        "status": status,
        "watched_at": WatchedDate(watched_at),
        "tmdb_id": defaults.get("tmdb_id"),
        "tmdb_rating": defaults.get("tmdb_rating"),
        "overview": defaults.get("overview"),
        "poster_url": defaults.get("poster_url"),
    }


def render_production_editor(productions: list[Production], on_save) -> None:
    """Editor inline de produções com data_editor."""
    import pandas as pd

    if not productions:
        return

    df_data = []
    for p in productions:
        df_data.append({
            "ID": p.id,
            "Nome": p.name,
            "Tipo": p.type.value,
            "Categoria": p.category.value,
            "Avaliação": p.rating.value,
            "Duração (min)": p.duration.minutes,
            "Temporadas": p.seasons.value,
            "Eps. Assistidos": p.episodes_watched.value,
            "Total Eps.": p.total_episodes.value,
            "Status": p.status.value,
            "Data": p.watched_at.value.isoformat(),
        })

    df = pd.DataFrame(df_data)

    column_config = {
        "ID": st.column_config.NumberColumn(disabled=True, width="small"),
        "Nome": st.column_config.TextColumn(width="large", required=True),
        "Tipo": st.column_config.SelectboxColumn(options=["Filme", "Série"], width="small", required=True),
        "Categoria": st.column_config.SelectboxColumn(options=[c.value for c in MediaCategory], width="medium", required=True),
        "Avaliação": st.column_config.NumberColumn(min_value=1, max_value=5, step=1, width="small", required=True),
        "Duração (min)": st.column_config.NumberColumn(min_value=1, step=1, width="small", required=True),
        "Temporadas": st.column_config.NumberColumn(min_value=1, max_value=50, step=1, width="small"),
        "Eps. Assistidos": st.column_config.NumberColumn(min_value=0, step=1, width="small"),
        "Total Eps.": st.column_config.NumberColumn(min_value=1, step=1, width="small"),
        "Status": st.column_config.SelectboxColumn(options=[s.value for s in MediaStatus], width="medium", required=True),
        "Data": st.column_config.DateColumn(width="small", required=True),
    }

    edited_df = st.data_editor(
        df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        key="editor_productions",
    )

    if not edited_df.equals(df):
        changes = 0
        for _, row in edited_df.iterrows():
            original = df[df["ID"] == row["ID"]].iloc[0]
            if not row.equals(original):
                on_save(row)
                changes += 1
        if changes:
            st.success(f"{changes} alteração(ões) salva(s)!")
            st.rerun()


def render_delete_section(productions: list[Production], on_delete) -> None:
    """Seção de exclusão com confirmação."""
    if not productions:
        return

    st.divider()
    st.subheader("🗑️ Excluir Produção")
    col_del1, col_del2, col_del3 = st.columns([3, 1, 1])
    with col_del1:
        id_to_delete = st.selectbox(
            "Selecione para excluir",
            options=[p.id for p in productions],
            format_func=lambda x: f"ID {x} | {next(p.name for p in productions if p.id == x)} ({next(p.type.value for p in productions if p.id == x)})",
            key="delete_select",
        )
    with col_del2:
        confirm = st.checkbox("Confirmo exclusão", key="delete_confirm")
    with col_del3:
        if st.button("Excluir Definitivamente", type="primary", use_container_width=True, disabled=not confirm):
            on_delete(id_to_delete)


def render_export_buttons(productions: list[Production], profile_name: str) -> None:
    """Botões de exportação CSV/JSON/Excel."""
    import pandas as pd
    import io
    from datetime import date

    if not productions:
        return

    st.divider()
    st.subheader("📤 Exportar Dados")

    df_data = []
    for p in productions:
        df_data.append({
            "ID": p.id,
            "Nome": p.name,
            "Tipo": p.type.value,
            "Categoria": p.category.value,
            "Avaliação": p.rating.value,
            "Duração (min)": p.duration.minutes,
            "Temporadas": p.seasons.value,
            "Eps. Assistidos": p.episodes_watched.value,
            "Total Eps.": p.total_episodes.value,
            "Status": p.status.value,
            "Data": p.watched_at.value.isoformat(),
        })
    df = pd.DataFrame(df_data)

    exp_col1, exp_col2, exp_col3 = st.columns(3)
    with exp_col1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 CSV", csv, f"painel_maratonista_{profile_name}_{date.today()}.csv", "text/csv", use_container_width=True)
    with exp_col2:
        json_str = df.to_json(orient="records", force_ascii=False, indent=2)
        st.download_button("📥 JSON", json_str, f"painel_maratonista_{profile_name}_{date.today()}.json", "application/json", use_container_width=True)
    with exp_col3:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Producoes")
        st.download_button("📥 Excel", excel_buffer.getvalue(), f"painel_maratonista_{profile_name}_{date.today()}.xlsx",
                          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)


def render_badges(badges: list[Badge], stats: Stats) -> None:
    """Renderiza badges conquistadas e progresso."""
    from ....domain.entities import BADGE_DEFINITIONS

    st.divider()
    st.subheader("🏅 Conquistas (Badges)")

    all_defs = BADGE_DEFINITIONS
    earned_keys = {b.key for b in badges}

    if badges:
        st.write("**Conquistadas:**")
        cols = st.columns(min(5, len(badges)))
        for i, badge in enumerate(badges):
            with cols[i % 5]:
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; border-radius: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; margin: 5px;">
                    <div style="font-size: 3rem;">{badge.emoji}</div>
                    <div style="font-weight: bold;">{badge.name}</div>
                    <div style="font-size: 0.8rem; opacity: 0.9;">{badge.description}</div>
                </div>
                """, unsafe_allow_html=True)

    with st.expander("📋 Ver todas as conquistas e progresso"):
        progress_data = [
            (BadgeKey.FIRST_STEPS, f"1 produção ({stats.total_productions}/1)"),
            (BadgeKey.MARATHONER, f"10 produções ({stats.total_productions}/10)"),
            (BadgeKey.CRITIC, f"5 notas máximas ({stats.perfect_scores}/5)"),
            (BadgeKey.BINGE_WATCHER, f"50 episódios ({stats.total_episodes_watched}/50)"),
            (BadgeKey.FILM_BUFF, f"20 filmes ({stats.movies_count}/20)"),
            (BadgeKey.SERIES_ADDICT, f"10 séries ({stats.series_count}/10)"),
            (BadgeKey.GENRE_EXPLORER, f"5 categorias ({stats.unique_categories}/5)"),
            (BadgeKey.TIME_LORD, f"5000 min ({stats.total_watch_time.minutes}/5000)"),
            (BadgeKey.COMPLETIONIST, f"10 séries completas ({stats.completed_series}/10)"),
        ]

        for key, progress in progress_data:
            badge_def = all_defs[key]
            done = key in earned_keys
            status = "🏆" if done else ("✅" if key in [BadgeKey.FIRST_STEPS] and stats.total_productions >= 1 else "🔒")
            if key == BadgeKey.MARATHONER and stats.total_productions >= 10: status = "✅"
            if key == BadgeKey.CRITIC and stats.perfect_scores >= 5: status = "✅"
            if key == BadgeKey.BINGE_WATCHER and stats.total_episodes_watched >= 50: status = "✅"
            if key == BadgeKey.FILM_BUFF and stats.movies_count >= 20: status = "✅"
            if key == BadgeKey.SERIES_ADDICT and stats.series_count >= 10: status = "✅"
            if key == BadgeKey.GENRE_EXPLORER and stats.unique_categories >= 5: status = "✅"
            if key == BadgeKey.TIME_LORD and stats.total_watch_time.minutes >= 5000: status = "✅"
            if key == BadgeKey.COMPLETIONIST and stats.completed_series >= 10: status = "✅"

            st.write(f"{status} **{badge_def['emoji']} {badge_def['name']}** — {badge_def['desc']}  \n   *{progress}*")