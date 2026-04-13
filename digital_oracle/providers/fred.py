from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ..http import JsonHttpClient, UrllibJsonClient
from ._coerce import _coerce_float, _coerce_int
from .base import ProviderParseError, SignalProvider

_BASE_URL = "https://api.stlouisfed.org/fred"


@dataclass(frozen=True)
class FredSeriesQuery:
    series_id: str
    observation_start: str | None = None
    observation_end: str | None = None
    limit: int | None = None
    sort_order: str = "desc"


@dataclass(frozen=True)
class FredObservation:
    date: str
    value: float


@dataclass
class FredSeries:
    series_id: str
    title: str | None
    frequency: str | None
    units: str | None
    observations: tuple[FredObservation, ...]


@dataclass(frozen=True)
class FredSearchQuery:
    search_text: str
    limit: int = 20


@dataclass(frozen=True)
class FredSeriesInfo:
    series_id: str
    title: str
    frequency: str | None
    units: str | None
    observation_start: str | None
    observation_end: str | None
    popularity: int | None


class FredProvider(SignalProvider):
    provider_id = "fred"
    display_name = "FRED (Federal Reserve Economic Data)"
    capabilities = ("economic_series", "series_search")

    def __init__(
        self,
        api_key: str,
        http_client: JsonHttpClient | None = None,
    ) -> None:
        self.api_key = api_key
        self.http_client = http_client or UrllibJsonClient()

    # ------------------------------------------------------------------
    # get_series
    # ------------------------------------------------------------------

    def get_series(self, query: FredSeriesQuery) -> FredSeries:
        params: dict[str, object] = {
            "series_id": query.series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "sort_order": query.sort_order,
            "observation_start": query.observation_start,
            "observation_end": query.observation_end,
            "limit": query.limit,
        }

        data = self.http_client.get_json(
            f"{_BASE_URL}/series/observations", params=params
        )

        raw_obs = data.get("observations") if isinstance(data, dict) else None
        if raw_obs is None:
            raise ProviderParseError("missing 'observations' in FRED response")

        observations: list[FredObservation] = []
        for item in raw_obs:
            val = _coerce_float(item.get("value"))
            if val is None:
                continue
            date = item.get("date", "")
            observations.append(FredObservation(date=date, value=val))

        title, frequency, units = self._fetch_series_meta(query.series_id)

        return FredSeries(
            series_id=query.series_id,
            title=title,
            frequency=frequency,
            units=units,
            observations=tuple(observations),
        )

    def _fetch_series_meta(
        self, series_id: str
    ) -> tuple[str | None, str | None, str | None]:
        try:
            data = self.http_client.get_json(
                f"{_BASE_URL}/series",
                params={
                    "series_id": series_id,
                    "api_key": self.api_key,
                    "file_type": "json",
                },
            )
            seriess = data.get("seriess", []) if isinstance(data, dict) else []
            if seriess:
                s = seriess[0]
                return (
                    s.get("title"),
                    s.get("frequency"),
                    s.get("units"),
                )
        except Exception:
            pass
        return None, None, None

    # ------------------------------------------------------------------
    # search_series
    # ------------------------------------------------------------------

    def search_series(self, query: FredSearchQuery) -> list[FredSeriesInfo]:
        params: dict[str, object] = {
            "search_text": query.search_text,
            "api_key": self.api_key,
            "file_type": "json",
            "limit": query.limit,
        }

        data = self.http_client.get_json(
            f"{_BASE_URL}/series/search", params=params
        )

        seriess = data.get("seriess", []) if isinstance(data, dict) else []

        results: list[FredSeriesInfo] = []
        for s in seriess:
            sid = s.get("id", "")
            title = s.get("title", "")
            if not sid:
                continue
            results.append(
                FredSeriesInfo(
                    series_id=sid,
                    title=title,
                    frequency=s.get("frequency"),
                    units=s.get("units"),
                    observation_start=s.get("observation_start"),
                    observation_end=s.get("observation_end"),
                    popularity=_coerce_int(s.get("popularity")),
                )
            )
        return results
