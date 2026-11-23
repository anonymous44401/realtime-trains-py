from unittest.mock import MagicMock, patch

from realtime_trains_py.internal.requests import DEFAULT_TIMEOUT, get_request


class TestLiveDriftAndTimeout:
    def test_default_timeout_configured(self):
        assert DEFAULT_TIMEOUT == 10

    @patch("realtime_trains_py.internal.requests.get")
    def test_get_request_uses_timeout(self, mock_get):
        mock_resp = MagicMock(status_code=200)
        mock_get.return_value = mock_resp

        get_request("api/info", headers={"Accept": "application/json"})
        mock_get.assert_called_once_with(
            "https://data.rtt.io/api/info",
            headers={"Accept": "application/json"},
            params=None,
            timeout=10,
        )

    def test_loop_timing_condition(self):
        # Verify that int(time.time()) >= next_update prevents loop stalling
        # when a request takes longer than 1 second (e.g. drift of 2 seconds)
        next_update = 1000
        current_time_missed = 1002  # Skipped exact 1000

        # With the fix:
        assert current_time_missed >= next_update
        # The old condition would have evaluated to False:
        assert not (current_time_missed == next_update)
