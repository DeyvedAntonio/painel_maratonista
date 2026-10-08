"""Implementação SQLite do ProfileRepository."""

from typing import Optional
import sqlite3
from ...data.database import Database
from ...domain.entities import Profile


class SQLiteProfileRepository:
    """Repositório de perfis usando SQLite."""

    def __init__(self, db: Database):
        self.db = db

    def get_all(self) -> list[Profile]:
        with self.db.connection() as conn:
            rows = conn.execute(
                "SELECT id, name, avatar_emoji, is_active, created_at FROM profiles WHERE is_active=1 ORDER BY id"
            ).fetchall()
            return [self._row_to_profile(row) for row in rows]

    def get_by_id(self, profile_id: int) -> Optional[Profile]:
        with self.db.connection() as conn:
            row = conn.execute(
                "SELECT id, name, avatar_emoji, is_active, created_at FROM profiles WHERE id=?",
                (profile_id,),
            ).fetchone()
            return self._row_to_profile(row) if row else None

    def get_default(self) -> Profile:
        with self.db.connection() as conn:
            row = conn.execute(
                "SELECT id, name, avatar_emoji, is_active, created_at FROM profiles WHERE id=1"
            ).fetchone()
            if row:
                return self._row_to_profile(row)
            # Fallback - cria se não existir
            return self.create(Profile.create("Principal", "🎬"))

    def create(self, profile: Profile) -> Profile:
        with self.db.connection() as conn:
            cursor = conn.execute(
                "INSERT INTO profiles (name, avatar_emoji) VALUES (?, ?)",
                (profile.name, profile.avatar_emoji),
            )
            return Profile(
                id=cursor.lastrowid,
                name=profile.name,
                avatar_emoji=profile.avatar_emoji,
                is_active=True,
            )

    def update(self, profile: Profile) -> Profile:
        with self.db.connection() as conn:
            conn.execute(
                "UPDATE profiles SET name=?, avatar_emoji=?, is_active=? WHERE id=?",
                (profile.name, profile.avatar_emoji, int(profile.is_active), profile.id),
            )
            return profile

    def delete(self, profile_id: int) -> bool:
        if profile_id == 1:
            return False  # Proteção do perfil padrão
        with self.db.connection() as conn:
            cursor = conn.execute("DELETE FROM profiles WHERE id=?", (profile_id,))
            return cursor.rowcount > 0

    @staticmethod
    def _row_to_profile(row: sqlite3.Row) -> Profile:
        return Profile(
            id=row["id"],
            name=row["name"],
            avatar_emoji=row["avatar_emoji"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
        )