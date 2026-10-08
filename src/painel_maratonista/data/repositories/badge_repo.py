"""Implementação SQLite do BadgeRepository."""

from typing import Optional
import sqlite3
from ...data.database import Database
from ...domain.entities import Badge
from ...domain.enums import BadgeKey


class SQLiteBadgeRepository:
    """Repositório de badges usando SQLite."""

    def __init__(self, db: Database):
        self.db = db

    def get_by_profile(self, profile_id: int) -> list[Badge]:
        with self.db.connection() as conn:
            rows = conn.execute(
                "SELECT id, profile_id, badge_key, badge_name, badge_emoji, description, earned_at FROM badges WHERE profile_id=? ORDER BY earned_at",
                (profile_id,),
            ).fetchall()
            return [self._row_to_badge(row) for row in rows]

    def get_earned_keys(self, profile_id: int) -> set[str]:
        with self.db.connection() as conn:
            rows = conn.execute(
                "SELECT badge_key FROM badges WHERE profile_id=?", (profile_id,)
            ).fetchall()
            return {row["badge_key"] for row in rows}

    def award(self, badge: Badge) -> Badge:
        with self.db.connection() as conn:
            cursor = conn.execute(
                """INSERT OR IGNORE INTO badges (profile_id, badge_key, badge_name, badge_emoji, description)
                VALUES (?, ?, ?, ?, ?)""",
                (badge.profile_id, badge.key.value, badge.name, badge.emoji, badge.description),
            )
            return Badge(
                id=cursor.lastrowid or badge.id,
                profile_id=badge.profile_id,
                key=badge.key,
                name=badge.name,
                emoji=badge.emoji,
                description=badge.description,
            )

    def has_badge(self, profile_id: int, badge_key: str) -> bool:
        with self.db.connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM badges WHERE profile_id=? AND badge_key=?",
                (profile_id, badge_key),
            ).fetchone()
            return row is not None

    @staticmethod
    def _row_to_badge(row: sqlite3.Row) -> Badge:
        return Badge(
            id=row["id"],
            profile_id=row["profile_id"],
            key=BadgeKey(row["badge_key"]),
            name=row["badge_name"],
            emoji=row["badge_emoji"],
            description=row["description"],
            earned_at=row["earned_at"],
        )