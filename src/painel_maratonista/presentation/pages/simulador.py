"""Página do Simulador de Maratona."""

import streamlit as st
from ....domain.value_objects import Duration


def render_simulador() -> None:
    """Renderiza página do Simulador de Maratona."""
    st.set_page_config(page_title="Simulador", page_icon="⏱️", layout="wide")

    st.subheader("⏱️ Simulador de Maratona")
    st.write("Planeje sua próxima maratona!")

    with st.form(key="simulador_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nome da série/filme", placeholder="Ex: Breaking Bad")
            quantity = st.number_input("Quantidade de episódios", min_value=1, step=1, value=10)
        with col2:
            avg_duration = st.number_input("Duração média por episódio (min)", min_value=1, max_value=300, step=1, value=45)
            daily_time = st.number_input(
                "Tempo disponível por dia (min)",
                min_value=1,
                max_value=720,
                step=15,
                value=60,
            )

        submitted = st.form_submit_button("🚀 Simular", use_container_width=True, type="primary")

    if submitted:
        if not name:
            st.error("Informe o nome da produção.")
            return

        total_minutes = quantity * avg_duration
        total_duration = Duration(total_minutes)
        days = total_minutes / daily_time

        st.success(
            f"🎯 **{name}**\n\n"
            f"📺 **Episódios:** {quantity}\n"
            f"⏱️ **Duração total:** {total_duration.formatted()} ({total_minutes} min)\n"
            f"📅 **Disponibilidade diária:** {daily_time} min\n\n"
            f"🗓️ **Tempo estimado:** **{days:.1f} dias** ({days/7:.1f} semanas)"
        )

        # Progress bar visual
        progress = min(1.0, daily_time / (avg_duration * quantity) * 100) if quantity > 0 else 0
        st.progress(min(1.0, days / 365))  # Progresso relativo a um ano

        # Dicas
        with st.expander("💡 Dicas"):
            st.markdown(f"""
            - Assista **{int(daily_time / avg_duration)} episódios por dia** para manter o ritmo
            - Em **{int(days)} dias** você termina (considerando {daily_time} min/dia)
            - Se assistir só nos fins de semana ({daily_time * 2} min), levará **{days * 5 / 2:.0f} dias corridos**
            - Marque no calendário: **término estimado em {days:.0f} dias**
            """)