"""Aplicação Principal - Painel Maratonista.

Arquitetura: Clean Architecture com Dependency Injection
- Domain: Entities, Value Objects, Enums
- Data: Repositories (SQLite)
- Services: Business Logic (Use Cases)
- Presentation: Streamlit Components & Pages
"""

import streamlit as st
from .config import get_settings
from .data.database import Database
from .services import ServiceContainer
from .services.tmdb_service import TMDBService
from .presentation.navigation import create_navigation


# Configuração da página (deve ser a primeira coisa)
st.set_page_config(
    page_title="Painel Maratonista",
    page_icon=":film_strip:",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_database() -> Database:
    """Singleton do banco de dados."""
    return Database()


@st.cache_resource
def get_service_container() -> ServiceContainer:
    """Container de serviços com DI."""
    db = get_database()
    return ServiceContainer(db)


@st.cache_resource
def get_tmdb_service() -> TMDBService:
    """Singleton do serviço TMDb."""
    return TMDBService()


def init_session_state():
    """Inicializa estado da sessão."""
    if "active_profile_id" not in st.session_state:
        container = get_service_container()
        default_profile = container.profile_service.get_default_profile()
        st.session_state["active_profile_id"] = default_profile.id


def main():
    """Ponto de entrada da aplicação."""
    init_session_state()

    # Obter serviços
    container = get_service_container()
    tmdb_service = get_tmdb_service()

    profile_service = container.profile_service
    production_service = container.production_service
    badge_service = container.badge_service

    # Perfil ativo
    active_profile_id = st.session_state["active_profile_id"]
    active_profile = profile_service.get_profile(active_profile_id)

    if not active_profile:
        # Fallback para perfil padrão
        active_profile = profile_service.get_default_profile()
        st.session_state["active_profile_id"] = active_profile.id
        active_profile_id = active_profile.id

    active_profile_name = active_profile.name

    # Guardar no session_state para acesso nas páginas
    st.session_state["active_profile_id"] = active_profile_id
    st.session_state["active_profile_name"] = active_profile_name
    st.session_state["production_service"] = production_service
    st.session_state["badge_service"] = badge_service
    st.session_state["profile_service"] = profile_service
    st.session_state["tmdb_service"] = tmdb_service

    # Navegação
    nav = create_navigation()
    nav.run()


if __name__ == "__main__":
    main()