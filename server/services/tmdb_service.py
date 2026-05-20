"""
MoodFlix — TMDB API Service
Handles all interactions with The Movie Database API.
"""

import requests
from config import get_config

config = get_config()

API_KEY = config.TMDB_API_KEY
BASE_URL = config.TMDB_BASE_URL
IMAGE_BASE = config.TMDB_IMAGE_BASE


def _get(endpoint: str, params: dict = None) -> dict | None:
    """Make a GET request to the TMDB API."""
    if not API_KEY:
        print("[TMDB] Warning: No API key configured.")
        return None

    url = f"{BASE_URL}{endpoint}"
    default_params = {"api_key": API_KEY, "language": "en-US"}
    if params:
        default_params.update(params)

    try:
        response = requests.get(url, params=default_params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[TMDB] API Error: {e}")
        return None


def get_poster_url(path: str, size: str = "w500") -> str:
    """Build full poster URL from a TMDB poster path."""
    if not path:
        return ""
    return f"{IMAGE_BASE}/{size}{path}"


def get_backdrop_url(path: str, size: str = "original") -> str:
    """Build full backdrop URL from a TMDB backdrop path."""
    if not path:
        return ""
    return f"{IMAGE_BASE}/{size}{path}"


def _format_movie(movie: dict) -> dict:
    """Format a raw TMDB movie object into our standard shape."""
    return {
        "tmdb_id": movie.get("id"),
        "title": movie.get("title", movie.get("name", "")),
        "overview": movie.get("overview", ""),
        "poster": get_poster_url(movie.get("poster_path")),
        "backdrop": get_backdrop_url(movie.get("backdrop_path")),
        "rating": movie.get("vote_average", 0),
        "vote_count": movie.get("vote_count", 0),
        "release_date": movie.get("release_date", movie.get("first_air_date", "")),
        "genre_ids": movie.get("genre_ids", []),
        "popularity": movie.get("popularity", 0),
        "media_type": movie.get("media_type", "movie"),
        "original_language": movie.get("original_language", "en"),
    }


def _format_movie_detail(movie: dict) -> dict:
    """Format a detailed TMDB movie object."""
    return {
        "tmdb_id": movie.get("id"),
        "title": movie.get("title", movie.get("name", "")),
        "tagline": movie.get("tagline", ""),
        "overview": movie.get("overview", ""),
        "poster": get_poster_url(movie.get("poster_path")),
        "backdrop": get_backdrop_url(movie.get("backdrop_path")),
        "rating": movie.get("vote_average", 0),
        "vote_count": movie.get("vote_count", 0),
        "release_date": movie.get("release_date", movie.get("first_air_date", "")),
        "genres": [g["name"] for g in movie.get("genres", [])],
        "runtime": movie.get("runtime", movie.get("episode_run_time", [0])),
        "budget": movie.get("budget", 0),
        "revenue": movie.get("revenue", 0),
        "status": movie.get("status", ""),
        "production_companies": [
            c["name"] for c in movie.get("production_companies", [])
        ],
        "spoken_languages": [
            l["english_name"] for l in movie.get("spoken_languages", [])
        ],
        "keywords": [],
        "cast": [],
        "crew": [],
        "videos": [],
        "similar": [],
        "reviews": [],
    }


# ---------------------------------------------------------------------------
# Public API methods
# ---------------------------------------------------------------------------

def get_trending(media_type: str = "all", time_window: str = "week", page: int = 1):
    """Get trending movies/shows."""
    data = _get(f"/trending/{media_type}/{time_window}", {"page": page})
    if not data:
        return {"results": [], "total_pages": 0}
    return {
        "results": [_format_movie(m) for m in data.get("results", [])],
        "total_pages": data.get("total_pages", 0),
        "page": data.get("page", 1),
    }


def get_popular(media_type: str = "movie", page: int = 1):
    """Get popular movies or TV shows."""
    data = _get(f"/{media_type}/popular", {"page": page})
    if not data:
        return {"results": [], "total_pages": 0}
    return {
        "results": [_format_movie(m) for m in data.get("results", [])],
        "total_pages": data.get("total_pages", 0),
        "page": data.get("page", 1),
    }


def get_top_rated(media_type: str = "movie", page: int = 1):
    """Get top-rated movies or TV shows."""
    data = _get(f"/{media_type}/top_rated", {"page": page})
    if not data:
        return {"results": [], "total_pages": 0}
    return {
        "results": [_format_movie(m) for m in data.get("results", [])],
        "total_pages": data.get("total_pages", 0),
        "page": data.get("page", 1),
    }


def get_movie_details(movie_id: int, media_type: str = "movie"):
    """Get full details for a movie or TV show."""
    data = _get(f"/{media_type}/{movie_id}", {
        "append_to_response": "credits,videos,similar,reviews,keywords"
    })
    if not data:
        return None

    result = _format_movie_detail(data)

    # Credits
    credits = data.get("credits", {})
    result["cast"] = [
        {
            "name": c["name"],
            "character": c.get("character", ""),
            "profile": get_poster_url(c.get("profile_path"), "w185"),
        }
        for c in credits.get("cast", [])[:15]
    ]
    result["crew"] = [
        {"name": c["name"], "job": c["job"]}
        for c in credits.get("crew", [])
        if c["job"] in ("Director", "Writer", "Screenplay", "Producer")
    ]

    # Videos (trailers)
    videos = data.get("videos", {}).get("results", [])
    result["videos"] = [
        {
            "name": v["name"],
            "key": v["key"],
            "site": v["site"],
            "type": v["type"],
        }
        for v in videos
        if v["site"] == "YouTube"
    ]

    # Similar
    similar = data.get("similar", {}).get("results", [])
    result["similar"] = [_format_movie(m) for m in similar[:12]]

    # Reviews
    reviews = data.get("reviews", {}).get("results", [])
    result["reviews"] = [
        {
            "author": r["author"],
            "content": r["content"][:500],
            "rating": r.get("author_details", {}).get("rating"),
            "created_at": r.get("created_at", ""),
        }
        for r in reviews[:5]
    ]

    # Keywords
    keywords_data = data.get("keywords", {})
    kw_list = keywords_data.get("keywords", keywords_data.get("results", []))
    result["keywords"] = [k["name"] for k in kw_list]

    return result


def search_movies(query: str, page: int = 1):
    """Search for movies and TV shows."""
    data = _get("/search/multi", {"query": query, "page": page})
    if not data:
        return {"results": [], "total_pages": 0}
    filtered = [
        _format_movie(m)
        for m in data.get("results", [])
        if m.get("media_type") in ("movie", "tv")
    ]
    return {
        "results": filtered,
        "total_pages": data.get("total_pages", 0),
        "page": data.get("page", 1),
    }


def discover_by_genres(genre_ids: list[int], media_type: str = "movie", page: int = 1):
    """Discover movies/shows by genre IDs."""
    data = _get(f"/discover/{media_type}", {
        "with_genres": ",".join(str(g) for g in genre_ids),
        "sort_by": "popularity.desc",
        "page": page,
    })
    if not data:
        return {"results": [], "total_pages": 0}
    return {
        "results": [_format_movie(m) for m in data.get("results", [])],
        "total_pages": data.get("total_pages", 0),
        "page": data.get("page", 1),
    }


def get_genres(media_type: str = "movie"):
    """Get the list of official genres."""
    data = _get(f"/genre/{media_type}/list")
    if not data:
        return []
    return data.get("genres", [])


# ---------------------------------------------------------------------------
# Mood → Genre mapping for the recommendation engine
# ---------------------------------------------------------------------------

MOOD_GENRE_MAP = {
    "happy": [35, 10402, 16, 10751],        # Comedy, Music, Animation, Family
    "sad": [18, 10749],                       # Drama, Romance
    "lonely": [18, 10749, 10751],            # Drama, Romance, Family
    "romantic": [10749, 35, 18],             # Romance, Comedy, Drama
    "excited": [28, 12, 878],                # Action, Adventure, Sci-Fi
    "relaxed": [35, 16, 10751, 99],          # Comedy, Animation, Family, Doc
    "stressed": [35, 16, 10402],             # Comedy, Animation, Music
    "dark": [53, 27, 80, 9648],              # Thriller, Horror, Crime, Mystery
    "emotional": [18, 10749, 36],            # Drama, Romance, History
    "mind-bending": [878, 9648, 53],         # Sci-Fi, Mystery, Thriller
    "curious": [99, 9648, 878, 36],          # Documentary, Mystery, Sci-Fi, History
    "nostalgic": [10751, 16, 35, 18],        # Family, Animation, Comedy, Drama
    "motivated": [18, 12, 36, 10752],        # Drama, Adventure, History, War
    "adventurous": [12, 28, 878, 14],        # Adventure, Action, Sci-Fi, Fantasy
    "wholesome": [10751, 16, 35, 10402],     # Family, Animation, Comedy, Music
    "scared": [27, 53, 9648],                # Horror, Thriller, Mystery
}


def get_movies_for_mood(mood: str, page: int = 1):
    """Get movies that match a specific mood via genre mapping."""
    mood_lower = mood.lower()
    genre_ids = MOOD_GENRE_MAP.get(mood_lower, [18, 35])
    return discover_by_genres(genre_ids, page=page)
