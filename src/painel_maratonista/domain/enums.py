"""Enums do domínio."""

from enum import Enum


class MediaType(str, Enum):
    """Tipo de mídia."""
    MOVIE = "Filme"
    SERIES = "Série"

    @classmethod
    def from_str(cls, value: str) -> "MediaType":
        """Converte string para enum (case-insensitive)."""
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        raise ValueError(f"Tipo inválido: {value}. Use 'Filme' ou 'Série'.")


class MediaStatus(str, Enum):
    """Status de visualização."""
    WATCHED = "Assistido"
    WATCHING = "Assistindo"
    PLAN_TO_WATCH = "Pretendo Assistir"
    DROPPED = "Abandonado"

    @classmethod
    def from_str(cls, value: str) -> "MediaStatus":
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        raise ValueError(f"Status inválido: {value}")


class MediaCategory(str, Enum):
    """Categorias/gêneros disponíveis."""
    ACTION = "Ação"
    ADVENTURE = "Aventura"
    COMEDY = "Comédia"
    DRAMA = "Drama"
    SCI_FI = "Ficção Científica"
    HORROR = "Terror"
    ROMANCE = "Romance"
    DOCUMENTARY = "Documentário"
    ANIMATION = "Animação"
    OTHER = "Outro"

    @classmethod
    def options(cls) -> list[str]:
        return [c.value for c in cls]

    @classmethod
    def from_str(cls, value: str) -> "MediaCategory":
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        return cls.OTHER

    @classmethod
    def from_tmdb_genre_ids(cls, genre_ids: list[int]) -> "MediaCategory":
        """Mapeia IDs de gênero do TMDb para nossas categorias."""
        tmdb_map = {
            28: cls.ACTION,
            12: cls.ADVENTURE,
            35: cls.COMEDY,
            18: cls.DRAMA,
            878: cls.SCI_FI,
            27: cls.HORROR,
            10749: cls.ROMANCE,
            99: cls.DOCUMENTARY,
            16: cls.ANIMATION,
        }
        for gid in genre_ids:
            if gid in tmdb_map:
                return tmdb_map[gid]
        return cls.OTHER


class BadgeKey(str, Enum):
    """Chaves das badges/conquistas."""
    FIRST_STEPS = "first_steps"
    MARATHONER = "marathoner"
    CRITIC = "critic"
    BINGE_WATCHER = "binge_watcher"
    FILM_BUFF = "film_buff"
    SERIES_ADDICT = "series_addict"
    GENRE_EXPLORER = "genre_explorer"
    TIME_LORD = "time_lord"
    COMPLETIONIST = "completionist"