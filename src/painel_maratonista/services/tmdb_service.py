"""TMDb Service - Integração com The Movie Database."""

import requests
from functools import lru_cache
from typing import Optional
from ..config import get_settings
from ..domain.enums import MediaType, MediaCategory


class TMDBService:
    """Cliente para API do TMDb."""

    def __init__(self, api_key: Optional[str] = None):
        self.settings = get_settings()
        self.api_key = api_key or self.settings.tmdb_api_key
        self.base_url = self.settings.tmdb_base_url
        self.image_base = self.settings.tmdb_image_base
        self.timeout = self.settings.tmdb_timeout
        self._session: Optional[requests.Session] = None

    @property
    def session(self) -> requests.Session:
        if self._session is None:
            self._session = requests.Session()
            if self.api_key:
                self._session.params = {"api_key": self.api_key, "language": "pt-BR"}
        return self._session

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def search_multi(self, query: str, page: int = 1) -> list[dict]:
        """Busca multi (filmes + séries)."""
        if not self.is_configured() or not query.strip():
            return []
        try:
            resp = self.session.get(
                f"{self.base_url}/search/multi",
                params={"query": query, "page": page, "include_adult": "false"},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            return [r for r in data.get("results", []) if r.get("media_type") in ("movie", "tv")]
        except Exception:
            return []

    def get_movie_details(self, movie_id: int) -> Optional[dict]:
        if not self.is_configured():
            return None
        try:
            resp = self.session.get(f"{self.base_url}/movie/{movie_id}", timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    def get_tv_details(self, tv_id: int) -> Optional[dict]:
        if not self.is_configured():
            return None
        try:
            resp = self.session.get(f"{self.base_url}/tv/{tv_id}", timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    @lru_cache(maxsize=128)
    def get_genres(self, media_type: str) -> dict[int, str]:
        if not self.is_configured():
            return {}
        try:
            endpoint = "genre/movie/list" if media_type == "movie" else "genre/tv/list"
            resp = self.session.get(f"{self.base_url}/{endpoint}", timeout=self.timeout)
            resp.raise_for_status()
            return {g["id"]: g["name"] for g in resp.json().get("genres", [])}
        except Exception:
            return {}

    def simplify_result(self, result: dict) -> dict:
        """Converte resultado bruto do TMDb para formato simplificado."""
        media_type = result.get("media_type")
        title = result.get("title") or result.get("name") or "Sem título"
        year = ""
        if media_type == "movie" and result.get("release_date"):
            year = result["release_date"][:4]
        elif media_type == "tv" and result.get("first_air_date"):
            year = result["first_air_date"][:4]

        genres = self.get_genres(media_type)
        genre_names = [genres.get(gid, "") for gid in result.get("genre_ids", [])]
        genre_str = ", ".join([g for g in genre_names if g]) or "Desconhecido"

        poster = result.get("poster_path")
        poster_url = f"{self.image_base}{poster}" if poster else None

        return {
            "tmdb_id": result["id"],
            "media_type": media_type,
            "title": title,
            "year": year,
            "genre": genre_str,
            "overview": result.get("overview", "")[:200],
            "poster_url": poster_url,
            "vote_average": result.get("vote_average", 0),
            "display": f"{title} ({year}) — {media_type.capitalize()} — {genre_str}",
        }

    def fetch_metadata(self, tmdb_id: int, media_type: str) -> Optional[dict]:
        """Busca metadados completos para preencher formulário."""
        if media_type == "movie":
            data = self.get_movie_details(tmdb_id)
            if not data:
                return None
            genres = self.get_genres("movie")
            genre_names = [genres.get(g["id"], "") for g in data.get("genres", [])]
            return {
                "name": data.get("title"),
                "type": MediaType.MOVIE,
                "category": MediaCategory.from_tmdb_genre_ids([g["id"] for g in data.get("genres", [])]),
                "duration": Duration(data.get("runtime", 0)),
                "total_episodes": EpisodeCount(1),
                "seasons": SeasonCount(1),
                "year": data.get("release_date", "")[:4] if data.get("release_date") else "",
                "overview": data.get("overview", ""),
                "poster_url": f"{self.image_base}{data['poster_path']}" if data.get("poster_path") else None,
                "tmdb_rating": data.get("vote_average", 0),
                "tmdb_id": data["id"],
            }
        elif media_type == "tv":
            data = self.get_tv_details(tmdb_id)
            if not data:
                return None
            genres = self.get_genres("tv")
            genre_names = [genres.get(g["id"], "") for g in data.get("genres", [])]
            return {
                "name": data.get("name"),
                "type": MediaType.SERIES,
                "category": MediaCategory.from_tmdb_genre_ids([g["id"] for g in data.get("genres", [])]),
                "duration": Duration(data.get("episode_run_time", [0])[0] if data.get("episode_run_time") else 45),
                "total_episodes": EpisodeCount(data.get("number_of_episodes", 0)),
                "seasons": SeasonCount(data.get("number_of_seasons", 1)),
                "year": data.get("first_air_date", "")[:4] if data.get("first_air_date") else "",
                "overview": data.get("overview", ""),
                "poster_url": f"{self.image_base}{data['poster_path']}" if data.get("poster_path") else None,
                "tmdb_rating": data.get("vote_average", 0),
                "tmdb_id": data["id"],
            }
        return None