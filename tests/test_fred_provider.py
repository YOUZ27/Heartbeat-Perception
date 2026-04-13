from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from digital_oracle.providers.fred import (
    FredProvider,
    FredSearchQuery,
    FredSeriesQuery,
)

SAMPLE_OBSERVATIONS_JSON = {
    "observations": [
        {"date": "2026-04-10", "value": "19.23"},
        {"date": "2026-04-09", "value": "21.05"},
        {"date": "2026-04-08", "value": "."},
    ]
}

SAMPLE_SERIES_META_JSON = {
    "seriess": [
        {
            "id": "VIXCLS",
            "title": "CBOE Volatility Index: VIX",
            "frequency": "Daily",
            "units": "Index",
        }
    ]
}

SAMPLE_SEARCH_JSON = {
    "seriess": [
        {
            "id": "VIXCLS",
            "title": "CBOE Volatility Index: VIX",
            "frequency": "Daily",
            "units": "Index",
            "observation_start": "1990-01-02",
            "observation_end": "2026-04-10",
            "popularity": 95,
        }
    ]
}

SAMPLE_EMPTY_OBSERVATIONS = {"observations": []}

SAMPLE_ALL_MISSING = {
    "observations": [
        {"date": "2026-04-10", "value": "."},
        {"date": "2026-04-09", "value": ""},
    ]
}


class FakeJsonClient:
    """Returns pre-configured JSON responses keyed by URL substring."""

    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        self.responses = responses or {}
        self.calls: list[tuple[str, Mapping[str, object] | None]] = []

    def get_json(self, url: str, *, params: Mapping[str, object] | None = None) -> Any:
        self.calls.append((url, params))
        for key, value in self.responses.items():
            if key in url:
                return value
        return {}


class FredProviderGetSeriesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = FakeJsonClient(
            {
                "series/observations": SAMPLE_OBSERVATIONS_JSON,
                "fred/series": SAMPLE_SERIES_META_JSON,
            }
        )
        self.provider = FredProvider(api_key="test_key", http_client=self.client)

    def test_parse_observations_skips_missing(self) -> None:
        result = self.provider.get_series(FredSeriesQuery(series_id="VIXCLS"))
        self.assertEqual(len(result.observations), 2)
        self.assertAlmostEqual(result.observations[0].value, 19.23)
        self.assertEqual(result.observations[0].date, "2026-04-10")
        self.assertAlmostEqual(result.observations[1].value, 21.05)

    def test_series_metadata(self) -> None:
        result = self.provider.get_series(FredSeriesQuery(series_id="VIXCLS"))
        self.assertEqual(result.series_id, "VIXCLS")
        self.assertEqual(result.title, "CBOE Volatility Index: VIX")
        self.assertEqual(result.frequency, "Daily")
        self.assertEqual(result.units, "Index")

    def test_empty_observations(self) -> None:
        client = FakeJsonClient(
            {
                "series/observations": SAMPLE_EMPTY_OBSERVATIONS,
                "fred/series": SAMPLE_SERIES_META_JSON,
            }
        )
        provider = FredProvider(api_key="test_key", http_client=client)
        result = provider.get_series(FredSeriesQuery(series_id="VIXCLS"))
        self.assertEqual(len(result.observations), 0)

    def test_all_missing_values(self) -> None:
        client = FakeJsonClient(
            {
                "series/observations": SAMPLE_ALL_MISSING,
                "fred/series": SAMPLE_SERIES_META_JSON,
            }
        )
        provider = FredProvider(api_key="test_key", http_client=client)
        result = provider.get_series(FredSeriesQuery(series_id="VIXCLS"))
        self.assertEqual(len(result.observations), 0)

    def test_api_key_in_params(self) -> None:
        self.provider.get_series(FredSeriesQuery(series_id="VIXCLS"))
        for url, params in self.client.calls:
            self.assertIsNotNone(params)
            assert params is not None
            self.assertEqual(params["api_key"], "test_key")

    def test_limit_and_sort_order_passed(self) -> None:
        self.provider.get_series(
            FredSeriesQuery(series_id="VIXCLS", limit=10, sort_order="asc")
        )
        url, params = self.client.calls[0]
        assert params is not None
        self.assertEqual(params["limit"], 10)
        self.assertEqual(params["sort_order"], "asc")


class FredProviderSearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = FakeJsonClient({"series/search": SAMPLE_SEARCH_JSON})
        self.provider = FredProvider(api_key="test_key", http_client=self.client)

    def test_search_parses_results(self) -> None:
        results = self.provider.search_series(FredSearchQuery(search_text="VIX"))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].series_id, "VIXCLS")
        self.assertEqual(results[0].title, "CBOE Volatility Index: VIX")
        self.assertEqual(results[0].frequency, "Daily")
        self.assertEqual(results[0].popularity, 95)
        self.assertEqual(results[0].observation_start, "1990-01-02")

    def test_search_empty(self) -> None:
        client = FakeJsonClient({"series/search": {"seriess": []}})
        provider = FredProvider(api_key="test_key", http_client=client)
        results = provider.search_series(FredSearchQuery(search_text="nonexistent"))
        self.assertEqual(len(results), 0)

    def test_search_passes_api_key(self) -> None:
        self.provider.search_series(FredSearchQuery(search_text="VIX"))
        url, params = self.client.calls[0]
        assert params is not None
        self.assertEqual(params["api_key"], "test_key")
        self.assertEqual(params["search_text"], "VIX")


class FredProviderMetadataTests(unittest.TestCase):
    def test_describe(self) -> None:
        provider = FredProvider(api_key="k", http_client=FakeJsonClient())
        meta = provider.describe()
        self.assertEqual(meta.provider_id, "fred")
        self.assertIn("FRED", meta.display_name)
        self.assertIn("economic_series", meta.capabilities)
        self.assertIn("series_search", meta.capabilities)


if __name__ == "__main__":
    unittest.main()
