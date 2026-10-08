"""Handlers de exceção para Streamlit."""

import streamlit as st
from painel_maratonista.exceptions import (
    DomainError,
    ValidationError,
    NotFoundError,
    ConflictError,
    BusinessRuleError,
    ExternalServiceError,
    DatabaseError,
)


def handle_domain_error(error: DomainError) -> None:
    """Converte DomainError em feedback visual do Streamlit."""
    if isinstance(error, ValidationError):
        st.error(f"❌ Validação: {error.message}")
        if error.details.get("field"):
            st.caption(f"Campo: {error.details['field']}")

    elif isinstance(error, NotFoundError):
        st.warning(f"⚠️ {error.message}")

    elif isinstance(error, ConflictError):
        st.error(f"⚠️ Conflito: {error.message}")

    elif isinstance(error, BusinessRuleError):
        st.error(f"🚫 Regra de negócio: {error.message}")
        if error.details.get("rule"):
            st.caption(f"Regra: {error.details['rule']}")

    elif isinstance(error, ExternalServiceError):
        st.error(f"🌐 Serviço externo indisponível: {error.message}")
        st.caption("Tente novamente mais tarde ou verifique sua conexão.")

    elif isinstance(error, DatabaseError):
        st.error(f"💾 Erro no banco de dados: {error.message}")
        st.caption("Se o problema persistir, reinicie a aplicação.")

    else:
        st.error(f"❌ Erro: {error.message}")


def safe_execute(func, *args, **kwargs):
    """Executa função capturando DomainErrors."""
    try:
        return func(*args, **kwargs)
    except DomainError as e:
        handle_domain_error(e)
        return None
    except Exception as e:
        st.error(f"💥 Erro inesperado: {type(e).__name__}: {e}")
        return None


def with_error_handling(func):
    """Decorator para handlers de páginas Streamlit."""
    def wrapper(*args, **kwargs):
        return safe_execute(func, *args, **kwargs)
    return wrapper