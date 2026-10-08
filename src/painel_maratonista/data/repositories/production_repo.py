"""Implementação SQLite do ProductionRepository."""

from typing import Optional
import sqlite3
from ...data.database import Database
from ...domain.entities import Production, Stats
from ...domain.enums import MediaType, MediaStatus, MediaCategory
from ...domain.value_objects import Rating, Duration, EpisodeCount, SeasonCount, WatchedDate
from ...config import get_settings


class SQLiteProductionRepository:
    """Repositório de produções usando SQLite."""

    def __init__(self, db: Database):
        self.db = db
        self.settings = get_settings()

    def get_all(self, profile_id: int) -> list[Production]:
        with self.db.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM productions WHERE profile_id=? ORDER BY watched_at DESC, created_at DESC",
                (profile_id,),
            ).fetchall()
            return [self._row_to_production(row) for row in rows]

    def get_by_id(self, profile_id: int, production_id: int) -> Optional[Production]:
        with self.db.connection() as conn:
            row = conn.execute(
                "SELECT * FROM productions WHERE profile_id=? AND id=?",
                (profile_id, production_id),
            ).fetchone()
            return self._row_to_production(row) if row else None

    def create(self, production: Production) -> Production:
        with self.db.connection() as conn:
            cursor = conn.execute(
                """INSERT INTO productions (
                    profile_id, name, type, category, rating, duration,
                    seasons, episodes_watched, total_episodes, status, watched_at,
                    tmdb_id, tmdb_rating, overview, poster_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    production.profile_id,
                    production.name,
                    production.type.value,
                    production.category.value,
                    production.rating.value,
                    production.duration.minutes,
                    production.seasons.value,
                    production.episodes_watched.value,
                    production.total_episodes.value,
                    production.status.value,
                    production.watched_at.value.isoformat(),
                    production.tmdb_id,
                    production.tmdb_rating,
                    production.overview,
                    production.poster_url,
                ),
            )
            return Production(
                id=cursor.lastrowid,
                profile_id=production.profile_id,
                name=production.name,
                type=production.type,
                category=production.category,
                rating=production.rating,
                duration=production.duration,
                seasons=production.seasons,
                episodes_watched=production.episodes_watched,
                total_episodes=production.total_episodes,
                status=production.status,
                watched_at=production.watched_at,
            )

    def update(self, production: Production) -> Production:
        with self.db.connection() as conn:
            conn.execute(
                """UPDATE productions SET
                    name=?, type=?, category=?, rating=?, duration=?,
                    seasons=?, episodes_watched=?, total_episodes=?, status=?, watched_at=?,
                    tmdb_id=?, tmdb_rating=?, overview=?, poster_url=?,
                    updated_at=CURRENT_TIMESTAMP
                WHERE id=? AND profile_id=?""",
                (
                    production.name,
                    production.type.value,
                    production.category.value,
                    production.rating.value,
                    production.duration.minutes,
                    production.seasons.value,
                    production.episodes_watched.value,
                    production.total_episodes.value,
                    production.status.value,
                    production.watched_at.value.isoformat(),
                    production.tmdb_id,
                    production.tmdb_rating,
                    production.overview,
                    production.poster_url,
                    production.id,
                    production.profile_id,
                ),
            )
            return production

    def delete(self, profile_id: int, production_id: int) -> bool:
        with self.db.connection() as conn:
            cursor = conn.execute(
                "DELETE FROM productions WHERE profile_id=? AND id=?",
                (profile_id, production_id),
            )
            return cursor.rowcount > 0

    def count_by_profile(self, profile_id: int) -> int:
        with self.db.connection() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM productions WHERE profile_id=?", (profile_id,)
            ).fetchone()[0]

    def get_stats(self, profile_id: int) -> Stats:
        with self.db.connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM productions WHERE profile_id=?", (profile_id,)).fetchone()[0]
            total_min = conn.execute("SELECT COALESCE(SUM(duration), 0) FROM productions WHERE profile_id=?", (profile_id,)).fetchone()[0]
            avg_rating = conn.execute("SELECT COALESCE(AVG(rating), 0) FROM productions WHERE profile_id=?", (profile_id,)).fetchone()[0]

            by_type = {r["type"]: r["cnt"] for r in conn.execute("SELECT type, COUNT(*) as cnt FROM productions WHERE profile_id=? GROUP BY type", (profile_id,)).fetchall()}
            by_category = {r["category"]: r["cnt"] for r in conn.execute("SELECT category, COUNT(*) as cnt FROM productions WHERE profile_id=? GROUP BY category ORDER BY cnt DESC", (profile_id,)).fetchall()}
            by_status = {r["status"]: r["cnt"] for r in conn.execute("SELECT status, COUNT(*) as cnt FROM productions WHERE profile_id=? GROUP BY status", (profile_id,)).fetchall()}

            top_longest = [self._row_to_production(r) for r in conn.execute("SELECT * FROM productions WHERE profile_id=? ORDER BY duration DESC LIMIT 5", (profile_id,)).fetchall()]
            top_rated = [self._row_to_production(r) for r in conn.execute("SELECT * FROM productions WHERE profile_id=? ORDER BY rating DESC, duration DESC LIMIT 5", (profile_id,)).fetchall()]

            timeline = [{"mes": r["mes"], "count": r["cnt"], "total_min": r["total_min"]} for r in conn.execute("SELECT strftime('%Y-%m', watched_at) as mes, COUNT(*) as cnt, COALESCE(SUM(duration), 0) as total_min FROM productions WHERE profile_id=? AND watched_at >= date('now', '-12 months') GROUP BY mes ORDER BY mes", (profile_id,)).fetchall()]

            movies_count = conn.execute("SELECT COUNT(*) FROM productions WHERE profile_id=? AND type='Filme'", (profile_id,)).fetchone()[0]
            series_count = conn.execute("SELECT COUNT(*) FROM productions WHERE profile_id=? AND type='Série'", (profile_id,)).fetchone()[0]
            completed_series = conn.execute("SELECT COUNT(*) FROM productions WHERE profile_id=? AND type='Série' AND episodes_watched >= total_episodes", (profile_id,)).fetchone()[0]
            total_eps = conn.execute("SELECT COALESCE(SUM(episodes_watched), 0) FROM productions WHERE profile_id=? AND type='Série'", (profile_id,)).fetchone()[0]
            unique_cats = conn.execute("SELECT COUNT(DISTINCT category) FROM productions WHERE profile_id=?", (profile_id,)).fetchone()[0]
            perfect_scores = conn.execute("SELECT COUNT(*) FROM productions WHERE profile_id=? AND rating=5", (profile_id,)).fetchone()[0]

        return Stats(
            total_productions=total,
            total_watch_time=Duration(total_min),
            average_rating=round(avg_rating, 2),
            by_type=by_type,
            by_category=by_category,
            by_status=by_status,
            top_longest=top_longest,
            top_rated=top_rated,
            timeline=timeline,
            movies_count=movies_count,
            series_count=series_count,
            completed_series=completed_series,
            total_episodes_watched=total_eps,
            unique_categories=unique_cats,
            perfect_scores=perfect_scores,
        )

    @staticmethod
    def _row_to_production(row: sqlite3.Row) -> Production:
        return Production(
            id=row["id"],
            profile_id=row["profile_id"],
            name=row["name"],
            type=MediaType.from_str(row["type"]),
            category=MediaCategory.from_str(row["category"]),
            rating=Rating(row["rating"]),
            duration=Duration(row["duration"]),
            seasons=SeasonCount(row["seasons"]),
            episodes_watched=EpisodeCount(row["episodes_watched"]),
            total_episodes=EpisodeCount(row["total_episodes"]),
            status=MediaStatus.from_str(row["status"]),
            watched_at=WatchedDate.fromisoformat(row["watched_at"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            tmdb_id=row["tmdb_id"],
            tmdb_rating=row["tmdb_rating"],
            overview=row["overview"],
            poster_url=row["poster_url"],
        )