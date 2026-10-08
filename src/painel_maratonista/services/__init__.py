"""Service layer - Business logic / Use Cases."""

from typing import Optional
from ..domain.entities import Profile, Production, Badge, Stats
from ..domain.enums import MediaType, MediaStatus, MediaCategory, BadgeKey
from ..domain.value_objects import Rating, Duration, EpisodeCount, SeasonCount, WatchedDate
from ..data.repositories import (
    SQLiteProfileRepository,
    SQLiteProductionRepository,
    SQLiteBadgeRepository,
)
from ..data.database import Database


class ProfileService:
    """Serviço de gerenciamento de perfis."""

    def __init__(self, repo: SQLiteProfileRepository):
        self.repo = repo

    def list_profiles(self) -> list[Profile]:
        return self.repo.get_all()

    def get_profile(self, profile_id: int) -> Optional[Profile]:
        return self.repo.get_by_id(profile_id)

    def get_default_profile(self) -> Profile:
        return self.repo.get_default()

    def create_profile(self, name: str, avatar_emoji: str = "👤") -> Profile:
        profile = Profile.create(name, avatar_emoji)
        return self.repo.create(profile)

    def update_profile(self, profile: Profile) -> Profile:
        return self.repo.update(profile)

    def delete_profile(self, profile_id: int) -> bool:
        if profile_id == 1:
            raise ValueError("Não é possível excluir o perfil padrão")
        return self.repo.delete(profile_id)


class ProductionService:
    """Serviço de gerenciamento de produções."""

    def __init__(
        self,
        repo: SQLiteProductionRepository,
        badge_service: Optional["BadgeService"] = None,
    ):
        self.repo = repo
        self.badge_service = badge_service

    def list_productions(self, profile_id: int) -> list[Production]:
        return self.repo.get_all(profile_id)

    def get_production(self, profile_id: int, production_id: int) -> Optional[Production]:
        return self.repo.get_by_id(profile_id, production_id)

    def create_production(
        self,
        profile_id: int,
        name: str,
        type_: MediaType,
        category: MediaCategory,
        rating: Rating,
        duration: Duration,
        seasons: SeasonCount,
        episodes_watched: EpisodeCount,
        total_episodes: EpisodeCount,
        status: MediaStatus,
        watched_at: WatchedDate,
        tmdb_id: Optional[int] = None,
        tmdb_rating: Optional[float] = None,
        overview: Optional[str] = None,
        poster_url: Optional[str] = None,
    ) -> Production:
        production = Production(
            id=0,
            profile_id=profile_id,
            name=name,
            type=type_,
            category=category,
            rating=rating,
            duration=duration,
            seasons=seasons,
            episodes_watched=episodes_watched,
            total_episodes=total_episodes,
            status=status,
            watched_at=watched_at,
            tmdb_id=tmdb_id,
            tmdb_rating=tmdb_rating,
            overview=overview,
            poster_url=poster_url,
        )
        created = self.repo.create(production)

        # Verificar badges após criar
        if self.badge_service:
            self.badge_service.check_and_award(profile_id)

        return created

    def update_production(self, production: Production) -> Production:
        updated = self.repo.update(production)

        # Verificar badges após atualizar
        if self.badge_service:
            self.badge_service.check_and_award(production.profile_id)

        return updated

    def delete_production(self, profile_id: int, production_id: int) -> bool:
        result = self.repo.delete(profile_id, production_id)

        if result and self.badge_service:
            self.badge_service.check_and_award(profile_id)

        return result

    def get_stats(self, profile_id: int) -> Stats:
        return self.repo.get_stats(profile_id)

    def count_productions(self, profile_id: int) -> int:
        return self.repo.count_by_profile(profile_id)


class BadgeService:
    """Serviço de gerenciamento de badges/conquistas."""

    def __init__(self, repo: SQLiteBadgeRepository, production_repo: SQLiteProductionRepository):
        self.repo = repo
        self.production_repo = production_repo
        self.thresholds = {
            BadgeKey.FIRST_STEPS: lambda stats: stats.total_productions >= 1,
            BadgeKey.MARATHONER: lambda stats: stats.total_productions >= 10,
            BadgeKey.CRITIC: lambda stats: stats.perfect_scores >= 5,
            BadgeKey.BINGE_WATCHER: lambda stats: stats.total_episodes_watched >= 50,
            BadgeKey.FILM_BUFF: lambda stats: stats.movies_count >= 20,
            BadgeKey.SERIES_ADDICT: lambda stats: stats.series_count >= 10,
            BadgeKey.GENRE_EXPLORER: lambda stats: stats.unique_categories >= 5,
            BadgeKey.TIME_LORD: lambda stats: stats.total_watch_time.minutes >= 5000,
            BadgeKey.COMPLETIONIST: lambda stats: stats.completed_series >= 10,
        }

    def get_badges(self, profile_id: int) -> list[Badge]:
        return self.repo.get_by_profile(profile_id)

    def get_earned_keys(self, profile_id: int) -> set[str]:
        return self.repo.get_earned_keys(profile_id)

    def check_and_award(self, profile_id: int) -> list[Badge]:
        """Verifica condições e concede badges não conquistados."""
        stats = self.production_repo.get_stats(profile_id)
        earned_keys = self.repo.get_earned_keys(profile_id)
        new_badges = []

        for badge_key, condition in self.thresholds.items():
            if badge_key.value not in earned_keys and condition(stats):
                badge = Badge.from_key(profile_id, badge_key)
                awarded = self.repo.award(badge)
                new_badges.append(awarded)

        return new_badges

    def get_all_definitions(self) -> dict[BadgeKey, dict]:
        from ..domain.entities import BADGE_DEFINITIONS
        return BADGE_DEFINITIONS


# Factory para criar serviços com dependências injetadas
class ServiceContainer:
    """Container de injeção de dependência simples."""

    def __init__(self, db: Database):
        self.db = db
        self._profile_repo: Optional[SQLiteProfileRepository] = None
        self._production_repo: Optional[SQLiteProductionRepository] = None
        self._badge_repo: Optional[SQLiteBadgeRepository] = None
        self._profile_service: Optional[ProfileService] = None
        self._production_service: Optional[ProductionService] = None
        self._badge_service: Optional[BadgeService] = None

    @property
    def profile_repo(self) -> SQLiteProfileRepository:
        if self._profile_repo is None:
            self._profile_repo = SQLiteProfileRepository(self.db)
        return self._profile_repo

    @property
    def production_repo(self) -> SQLiteProductionRepository:
        if self._production_repo is None:
            self._production_repo = SQLiteProductionRepository(self.db)
        return self._production_repo

    @property
    def badge_repo(self) -> SQLiteBadgeRepository:
        if self._badge_repo is None:
            self._badge_repo = SQLiteBadgeRepository(self.db)
        return self._badge_repo

    @property
    def badge_service(self) -> BadgeService:
        if self._badge_service is None:
            self._badge_service = BadgeService(self.badge_repo, self.production_repo)
        return self._badge_service

    @property
    def profile_service(self) -> ProfileService:
        if self._profile_service is None:
            self._profile_service = ProfileService(self.profile_repo)
        return self._profile_service

    @property
    def production_service(self) -> ProductionService:
        if self._production_service is None:
            self._production_service = ProductionService(
                self.production_repo, self.badge_service
            )
        return self._production_service