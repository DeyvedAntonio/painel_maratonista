"""Página de Cadastro de Produções."""

import streamlit as st
from ..components import render_production_form
from ....domain.enums import MediaType, MediaCategory
from datetime import date


def render_cadastro():
    """Renderiza página de cadastro."""
    # Serviços do session_state
    production_service = st.session_state["production_service"]
    tmdb_service = st.session_state["tmdb_service"]
    active_profile_id = st.session_state["active_profile_id"]
    active_profile_name = st.session_state["active_profile_name"]

    st.subheader(f"📝 Cadastrar Nova Produção — {active_profile_name}")

    # --- Busca TMDb (fora do form) ---
    st.markdown("### 🔍 Buscar no TMDb (Preenchimento Automático)")

    if not tmdb_service.is_configured():
        st.info(
            "💡 Configure `TMDB_API_KEY` no `.env` para habilitar busca automática. "
            "Obtenha sua chave grátis em [themoviedb.org](https://www.themoviedb.org/settings/api)."
        )
    else:
        search_query = st.text_input(
            "Digite o nome da série/filme:",
            placeholder="Ex: Breaking Bad, Interestelar, The Office...",
            key="tmdb_search_input",
        )

        if search_query:
            with st.spinner("Buscando..."):
                results = tmdb_service.search_multi(search_query)

            if results:
                simplified = [tmdb_service.simplify_result(r) for r in results[:10]]

                selected = st.selectbox(
                    "Resultados:",
                    options=simplified,
                    format_func=lambda x: x["display"],
                    key="tmdb_select_result",
                )

                if selected and st.button("✨ Preencher Formulário", use_container_width=True, type="primary"):
                    with st.spinner("Carregando detalhes..."):
                        meta = tmdb_service.fetch_metadata(selected["tmdb_id"], selected["media_type"])

                    if meta:
                        form_data = {
                            "name": meta.get("name", ""),
                            "type": meta.get("type", MediaType.SERIES),
                            "category": meta.get("category", MediaCategory.OTHER),
                            "duration": meta.get("duration", 0),
                            "total_episodes": meta.get("total_episodes", 10),
                            "seasons": meta.get("seasons", 1),
                            "episodes_watched": 0,
                            "status": "Assistido",
                            "watched_at": date.today(),
                            "tmdb_id": meta.get("tmdb_id"),
                            "tmdb_rating": meta.get("tmdb_rating"),
                            "overview": meta.get("overview"),
                            "poster_url": meta.get("poster_url"),
                        }
                        for k, v in form_data.items():
                            st.session_state[f"form_{k}"] = v
                        st.success("Dados carregados! Revise e salve abaixo.")
                        st.rerun()
                    else:
                        st.error("Erro ao buscar detalhes completos.")
            else:
                st.caption("Nenhum resultado encontrado.")

    st.divider()

    # --- Formulário Principal ---
    with st.form(key="cadastro_form", clear_on_submit=False):
        st.subheader("✏️ Formulário de Cadastro")

        form_data = {k.replace("form_", ""): v for k, v in st.session_state.items() if k.startswith("form_")}
        defaults = form_data if form_data else {}

        data = render_production_form(
            production=None,
            tmdb_data=defaults,
        )

        submitted = st.form_submit_button("💾 Registrar", use_container_width=True, type="primary")

    if submitted:
        if not data["name"]:
            st.error("Por favor, insira o nome da série ou filme.")
            return

        try:
            for k in list(st.session_state.keys()):
                if k.startswith("form_"):
                    del st.session_state[k]

            production = production_service.create_production(
                profile_id=active_profile_id,
                **data,
            )
            st.success(
                f"✅ Registrado: **{production.name}** ({production.type.value}, {production.category.value}) — "
                f"Nota {production.rating}, {production.duration.formatted()}, Status: {production.status.value}"
            )
            st.balloons()
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")