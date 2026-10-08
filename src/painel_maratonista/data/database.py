"""Database connection e schema management."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from ..config import get_settings


SCHEMA = """
-- Perfis
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    avatar_emoji TEXT DEFAULT '👤',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Produções
CREATE TABLE IF NOT EXISTS productions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('Filme', 'Série')),
    category TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    duration INTEGER NOT NULL CHECK (duration >= 0),
    seasons INTEGER DEFAULT 1,
    episodes_watched INTEGER DEFAULT 0,
    total_episodes INTEGER DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'Assistido' CHECK (status IN ('Assistido', 'Assistindo', 'Pretendo Assistir', 'Abandonado')),
    watched_at DATE NOT NULL DEFAULT (date('now')),
    tmdb_id INTEGER,
    tmdb_rating REAL,
    overview TEXT,
    poster_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Badges
CREATE TABLE IF NOT EXISTS badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    badge_key TEXT NOT NULL,
    badge_name TEXT NOT NULL,
    badge_emoji TEXT NOT NULL,
    description TEXT,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(profile_id, badge_key)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_productions_profile ON productions(profile_id);
CREATE INDEX IF NOT EXISTS idx_productions_watched_at ON productions(watched_at);
CREATE INDEX IF NOT EXISTS idx_productions_category ON productions(category);
CREATE INDEX IF NOT EXISTS idx_productions_type ON productions(type);
CREATE INDEX IF NOT EXISTS idx_productions_status ON productions(status);
CREATE INDEX IF NOT EXISTS idx_badges_profile ON badges(profile_id);
"""


class Database:
    """Gerenciador de conexão SQLite."""

    def __init__(self, path: Path | None = None):
        self.path = path or get_settings().database_path
        self._init_db()

    def _init_db(self) -> None:
        """Inicializa schema e cria perfil padrão."""
        with self.connection() as conn:
            conn.executescript(SCHEMA)
            # Perfil padrão
            conn.execute(
                "INSERT OR IGNORE INTO profiles (id, name, avatar_emoji) VALUES (1, 'Principal', '🎬')"
            )
            conn.commit()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        """Context manager para conexão."""
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute_script(self, script: str) -> None:
        """Executa script SQL arbitrário."""
        with self.connection() as conn:
            conn.executescript(script)