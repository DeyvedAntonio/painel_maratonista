"""Presentation layer exports."""

from .components import (
    render_profile_selector,
    render_profile_management,
    render_metric_cards,
    render_charts_tabs,
    render_production_form,
    render_production_editor,
    render_delete_section,
    render_export_buttons,
    render_badges,
)
from .pages import home, cadastro, painel, simulador
from .navigation import create_navigation

__all__ = [
    # Components
    "render_profile_selector",
    "render_profile_management",
    "render_metric_cards",
    "render_charts_tabs",
    "render_production_form",
    "render_production_editor",
    "render_delete_section",
    "render_export_buttons",
    "render_badges",
    # Pages
    "home",
    "cadastro",
    "painel",
    "simulador",
    # Navigation
    "create_navigation",
]