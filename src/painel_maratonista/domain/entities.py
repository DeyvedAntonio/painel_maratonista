"""Entidades do domínio - Modelos ricos com validação."""

from dataclasses import dataclass
from datetime import date
from typing import Optional

from .enums import MediaType, MediaStatus, MediaCategory, BadgeKey
from .value_objects import Rating, Duration, EpisodeCount, SeasonCount, WatchedDate


@dataclass(slots=True)
class Profile:
    """Perfil de usuário."""
    id: int
    name: str
    avatar_emoji: str = "👤"
    is_active: bool = True
    created_at: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Nome do perfil não pode ser vazio")
        if len(self.name) > 50:
            raise ValueError("Nome do perfil muito longo (máx 50 chars)")
        self.name = self.name.strip()

    @classmethod
    def create(cls, name: str, avatar_emoji: str = "👤") -> "Profile":
        """Factory para novo perfil."""
        return cls(id=0, name=name, avatar_emoji=avatar_emoji)


@dataclass(slots=True)
class Production:
    """Produção (Filme ou Série) - Agregado raiz."""
    id: int
    profile_id: int
    name: str
    type: MediaType
    category: MediaCategory
    rating: Rating
    duration: Duration
    seasons: SeasonCount
    episodes_watched: EpisodeCount
    total_episodes: EpisodeCount
    status: MediaStatus
    watched_at: WatchedDate
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    # TMDB metadata (opcional)
    tmdb_id: Optional[int] = None
    tmdb_rating: Optional[float] = None
    overview: Optional[str] = None
    poster_url: Optional[str] = None

    def __post_init__(self) -> None:
        # Validações de consistência
        if self.type == MediaType.MOVIE:
            if self.seasons.value != 1:
                raise ValueError("Filmes devem ter exatamente 1 temporada")
            if self.total_episodes.value != 1:
                raise ValueError("Filmes devem ter exatamente 1 episódio")
            if self.episodes_watched.value > 1:
                raise ValueError("Episódios assistidos não pode exceder 1 para filmes")

        if self.episodes_watched.value > self.total_episodes.value:
            raise ValueError("Episódios assistidos não pode exceder total")

        if not self.name or not self.name.strip():
            raise ValueError("Nome da produção não pode ser vazio")

        self.name = self.name.strip()

    @property
    def is_completed(self) -> bool:
        """Verifica se a produção foi completada."""
        return self.episodes_watched.value >= self.total_episodes.value

    @property
    def progress_percentage(self) -> float:
        """Porcentagem de progresso (0-100)."""
        if self.total_episodes.value == 0:
            return 0.0
        return min(100.0, (self.episodes_watched.value / self.total_episodes.value) * 100)

    @property
    def total_watch_time(self) -> Duration:
        """Tempo total assistido (episódios * duração média)."""
        return Duration(self.episodes_watched.value * self.duration.minutes)

    @property
    def remaining_episodes(self) -> int:
        """Episódios restantes."""
        return max(0, self.total_episodes.value - self.episodes_watched.value)

    @property
    def estimated_days_to_complete(self, daily_minutes: int) -> float:
        """Estima dias para completar baseado em minutos/dia."""
        if daily_minutes <= 0:
            raise ValueError("Minutos diários deve ser positivo")
        remaining_time = self.remaining_episodes * self.duration.minutes
        return remaining_time / daily_minutes

    def mark_episode_watched(self) -> "Production":
        """Retorna nova instância com +1 episódio assistido."""
        if self.episodes_watched.value >= self.total_episodes.value:
            raise ValueError("Já completou todos os episódios")
        return Production(
            id=self.id,
            profile_id=self.profile_id,
            name=self.name,
            type=self.type,
            category=self.category,
            rating=self.rating,
            duration=self.duration,
            seasons=self.seasons,
            episodes_watched=EpisodeCount(self.episodes_watched.value + 1),
            total_episodes=self.total_episodes,
            status=MediaStatus.WATCHING if self.episodes_watched.value + 1 < self.total_episodes.value else MediaStatus.WATCHED,
            watched_at=self.watched_at,
            created_at=self.created_at,
            updated_at=None,
            tmdb_id=self.tmdb_id,
            tmdb_rating=self.tmdb_rating,
            overview=self.overview,
            poster_url=self.poster_url,
        )

    def update_rating(self, new_rating: Rating) -> "Production":
        """Retorna nova instância com nota atualizada."""
        return Production(
            id=self.id,
            profile_id=self.profile_id,
            name=self.name,
            type=self.type,
            category=self.category,
            rating=new_rating,
            duration=self.duration,
            seasons=self.seasons,
            episodes_watched=self.episodes_watched,
            total_episodes=self.total_episodes,
            status=self.status,
            watched_at=self.watched_at,
            created_at=self.created_at,
            updated_at=None,
            tmdb_id=self.tmdb_id,
            tmdb_rating=self.tmdb_rating,
            overview=self.overview,
            poster_url=self.poster_url,
        )


# Definições de badges (fora da classe para evitar mutable default)
BADGE_DEFINITIONS: dict[BadgeKey, dict[str, str]] = {
    BadgeKey.FIRST_STEPS: {"name": "Primeiros Passos", "emoji": "👶", "desc": "Cadastrou a primeira produção"},
    BadgeKey.MARATHONER: {"name": "Maratonista", "emoji": "🏃", "desc": "Assistiu 10+ produções"},
    BadgeKey.CRITIC: {"name": "Crítico", "emoji": "🎭", "desc": "Deu nota 5 para 5+ produções"},
    BadgeKey.BINGE_WATCHER: {"name": "Binge Watcher", "emoji": "🍿", "desc": "Assistiu 50+ episódios no total"},
    BadgeKey.FILM_BUFF: {"name": "Cinéfila", "emoji": "🎬", "desc": "Assistiu 20+ filmes"},
    BadgeKey.SERIES_ADDICT: {"name": "Viciado em Séries", "emoji": "📺", "desc": "Assistiu 10+ séries"},
    BadgeKey.GENRE_EXPLORER: {"name": "Explorador de Gêneros", "emoji": "🌈", "desc": "Assistiu produções de 5+ categorias diferentes"},
    BadgeKey.TIME_LORD: {"name": "Senhor do Tempo", "emoji": "⏰", "desc": "Acumulou 5000+ minutos assistidos"},
    BadgeKey.COMPLETIONIST: {"name": "Completionista", "emoji": "✅", "desc": "Completou 10+ séries (todos episódios)"},
}


@dataclass(slots=True)
class Badge:
    """Badge/Conquista."""
    id: int
    profile_id: int
    key: BadgeKey
    name: str
    emoji: str
    description: str
    earned_at: Optional[str] = None

    @classmethod
    def from_key(cls, profile_id: int, key: BadgeKey) -> "Badge":
        """Cria badge a partir da chave."""
        defs = BADGE_DEFINITIONS[key]
        return cls(
            id=0,
            profile_id=profile_id,
            key=key,
            name=defs["name"],
            emoji=defs["emoji"],
            description=defs["desc"],
        )


@dataclass(slots=True)
class Stats:
    """Estatísticas agregadas do perfil."""
    total_productions: int
    total_watch_time: Duration
    average_rating: float
    by_type: dict[str, int]
    by_category: dict[str, int]
    by_status: dict[str, int]
    top_longest: list[Production]
    top_rated: list[Production]
    timeline: list[dict]
    movies_count: int
    series_count: int
    completed_series: int
    total_episodes_watched: int
    unique_categories: int
    perfect_scores: int