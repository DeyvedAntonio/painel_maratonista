"""Configuração de navegação do Streamlit."""

import streamlit as st
from .pages import home, cadastro, painel, simulador


def create_navigation():
    """Cria estrutura de navegação do Streamlit."""
    pages = {
        "🏠 Início": [
            st.Page(home.render_home, title="Home", icon="🏠"),
        ],
        "📝 Cadastro": [
            st.Page(cadastro.render_cadastro, title="Nova Produção", icon="📝"),
        ],
        "📊 Dashboard": [
            st.Page(painel.render_painel, title="Dashboard", icon="🔥"),
        ],
        "⏱️ Simulador": [
            st.Page(simulador.render_simulador, title="Simulador", icon="⏱️"),
        ],
    }
    return st.navigation(pages, position="top")