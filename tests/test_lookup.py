from unittest.mock import MagicMock, patch

import pytest

from realtime_trains_py import RealtimeTrainsPy
from realtime_trains_py.internal.details import LookupData
from realtime_trains_py.parsing.lookup import code_lookup, location_lookup, lookup_check

MOCK_LOOKUP_PAYLOAD = {
    "locations": [
        {"longCode": "STEVNGE", "shortCode": "SVG", "description": "Stevenage"},
        {"longCode": "STEVNGE", "description": "Stevenage"},  # Duplicate entry
        {"longCode": "LIVST", "shortCode": "LST", "description": "London Liverpool Street"},
        {"longCode": "LIVSTLL", "description": "London Liverpool Street"},
        {"longCode": "KNGX", "shortCode": "KGX", "description": "London Kings Cross"},
    ]
}


class TestCodeLookup:
    def test_deduplication(self):
        # STEVNGE appears twice for Stevenage; should return only 1 LookupData
        results = code_lookup("STEVNGE", MOCK_LOOKUP_PAYLOAD, raw=True)
        assert len(results) == 1
        assert results[0] == LookupData("STEVNGE", "Stevenage")

    def test_short_code_match(self):
        results = code_lookup("SVG", MOCK_LOOKUP_PAYLOAD, raw=True)
        assert len(results) == 1
        assert results[0] == LookupData("SVG", "Stevenage")

    def test_unknown_code(self):
        results = code_lookup("UNKNOWN", MOCK_LOOKUP_PAYLOAD, raw=True)
        assert results == []


class TestLocationLookup:
    def test_matches_multiple_codes(self):
        results = location_lookup("Liverpool Street", MOCK_LOOKUP_PAYLOAD, raw=True)
        codes = [item.code for item in results]
        assert "LST" in codes
        assert "LIVST" in codes
        assert "LIVSTLL" in codes


class TestLookupCheck:
    def test_case_insensitive_description(self):
        # Description in lowercase should match "Stevenage"
        assert lookup_check("SVG", "stevenage", MOCK_LOOKUP_PAYLOAD, raw=True) is True
        assert lookup_check("SVG", "STEVENAGE", MOCK_LOOKUP_PAYLOAD, raw=True) is True
        assert lookup_check("svg", "Stevenage", MOCK_LOOKUP_PAYLOAD, raw=True) is True

    def test_non_matching_pair(self):
        assert lookup_check("SVG", "London Kings Cross", MOCK_LOOKUP_PAYLOAD, raw=True) is False


class TestRealtimeTrainsPyLookup:
    @patch("realtime_trains_py.internal.requests.get")
    def test_lookup_raw_true_unreachable_branch_fixed(self, mock_get):
        # Mock auth check and data request
        auth_resp = MagicMock(status_code=200)
        auth_resp.json.return_value = {"token": "dummy"}

        data_resp = MagicMock(status_code=200)
        data_resp.json.return_value = MOCK_LOOKUP_PAYLOAD

        mock_get.side_effect = [auth_resp, data_resp]

        rtt = RealtimeTrainsPy(request_token="token123")
        res = rtt.lookup(raw=True)

        # Must return the raw dictionary, not [LookupData("", "")]
        assert isinstance(res, dict)
        assert "locations" in res
        assert res["locations"] == MOCK_LOOKUP_PAYLOAD["locations"]

    @patch("realtime_trains_py.save_file")
    @patch("realtime_trains_py.internal.requests.get")
    def test_lookup_saves_file_when_not_raw(self, mock_get, mock_save):
        auth_resp = MagicMock(status_code=200)
        data_resp = MagicMock(status_code=200)
        data_resp.json.return_value = MOCK_LOOKUP_PAYLOAD
        mock_get.side_effect = [auth_resp, data_resp]

        mock_save.return_value = "realtime_trains_py_data/2026-11-23_lookup_data.json"

        rtt = RealtimeTrainsPy(request_token="token123")
        res = rtt.lookup(raw=False)

        mock_save.assert_called_once()
        assert res == "realtime_trains_py_data/2026-11-23_lookup_data.json"
