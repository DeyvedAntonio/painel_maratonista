"""Value Objects - Objetos de valor imutáveis com validação."""

from dataclasses import dataclass
from datetime import date
from typing import Self


@dataclass(frozen=True, slots=True)
class Rating:
    """Nota de avaliação (1-5)."""
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int):
            raise TypeError(f"Rating deve ser int, recebeu {type(self.value).__name__}")
        if not 1 <= self.value <= 5:
            raise ValueError(f"Rating deve estar entre 1 e 5, recebeu {self.value}")

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return "⭐" * self.value

    @classmethod
    def from_tmdb(cls, tmdb_rating: float) -> Self:
        """Converte nota TMDb (0-10) para nossa escala (1-5)."""
        if tmdb_rating <= 0:
            return cls(3)
        return cls(max(1, min(5, round(tmdb_rating / 2))))


@dataclass(frozen=True, slots=True)
class Duration:
    """Duração em minutos (positiva)."""
    minutes: int

    def __post_init__(self) -> None:
        if not isinstance(self.minutes, int):
            raise TypeError(f"Duration deve ser int, recebeu {type(self.minutes).__name__}")
        if self.minutes < 0:
            raise ValueError(f"Duration não pode ser negativo: {self.minutes}")

    def __int__(self) -> int:
        return self.minutes

    def __add__(self, other: "Duration") -> "Duration":
        return Duration(self.minutes + other.minutes)

    def formatted(self) -> str:
        """Retorna formato legível (ex: '2h 30min')."""
        hours, mins = divmod(self.minutes, 60)
        if hours:
            return f"{hours}h {mins}min" if mins else f"{hours}h"
        return f"{mins}min"


@dataclass(frozen=True, slots=True)
class EpisodeCount:
    """Contagem de episódios (não-negativa)."""
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int):
            raise TypeError(f"EpisodeCount deve ser int, recebeu {type(self.value).__name__}")
        if self.value < 0:
            raise ValueError(f"EpisodeCount não pode ser negativo: {self.value}")

    def __int__(self) -> int:
        return self.value


@dataclass(frozen=True, slots=True)
class SeasonCount:
    """Contagem de temporadas (positiva)."""
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int):
            raise TypeError(f"SeasonCount deve ser int, recebeu {type(self.value).__name__}")
        if self.value < 1:
            raise ValueError(f"SeasonCount deve ser >= 1: {self.value}")

    def __int__(self) -> int:
        return self.value


@dataclass(frozen=True, slots=True)
class WatchedDate:
    """Data de visualização (não futura)."""
    value: date

    def __post_init__(self) -> None:
        if not isinstance(self.value, date):
            raise TypeError(f"WatchedDate deve ser date, recebeu {type(self.value).__name__}")
        if self.value > date.today():
            raise ValueError(f"Data não pode ser futura: {self.value}")

    def __str__(self) -> str:
        return self.value.isoformat()

    @classmethod
    def today(cls) -> Self:
        return cls(date.today())

    @classmethod
    def fromisoformat(cls, date_str: str) -> Self:
        """Cria WatchedDate a partir de string ISO (YYYY-MM-DD)."""
        return cls(date.fromisoformat(date_str))