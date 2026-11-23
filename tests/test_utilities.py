import datetime as dt
import pytest

from realtime_trains_py.internal.errors import (
    InvalidDateProvided,
    InvalidTimeProvided,
    InvalidTIPLOCProvided,
)
from realtime_trains_py.internal.utilities import (
    check_cancel,
    check_delay,
    create_parameters,
    fmt,
    validate_date,
    validate_time,
    validate_tiploc,
    validate_uid,
)


class TestCheckDelay:
    def test_on_time(self):
        assert check_delay("10:00", "10:00") == 0

    def test_daytime_delay(self):
        assert check_delay("10:00", "10:15") == 900

    def test_daytime_early(self):
        assert check_delay("10:15", "10:00") == -900

    def test_midnight_crossover_late(self):
        # Scheduled 23:55, expected 00:05 -> 10 minutes late (+600s)
        assert check_delay("23:55", "00:05") == 600

    def test_midnight_crossover_early(self):
        # Scheduled 00:05, expected 23:55 -> 10 minutes early (-600s)
        assert check_delay("00:05", "23:55") == -600

    def test_midnight_multi_hour_delay(self):
        # Scheduled 23:00, expected 01:30 -> 2.5 hours late (+9000s)
        assert check_delay("23:00", "01:30") == 9000


class TestCheckCancel:
    def test_cancelled(self):
        res = check_cancel("Cancelled")
        assert fmt["red"] in res
        assert "Cancelled" in res

    def test_on_time(self):
        res = check_cancel("On time")
        assert fmt["green"] in res
        assert "On time" in res

    def test_midnight_delay_colour(self):
        # 10 min late (600s) across midnight should be purple, not cyan
        res = check_cancel("Exp 00:05", scheduled="23:55")
        assert fmt["purple"] in res
        assert "00:05" in res

    def test_severe_delay_colour(self):
        # 25 min late (1500s) should be red
        res = check_cancel("Exp 10:25", scheduled="10:00")
        assert fmt["red"] in res

    def test_early_colour(self):
        # Running early should be cyan
        res = check_cancel("Exp 09:55", scheduled="10:00")
        assert fmt["cyan"] in res


class TestCreateParameters:
    def test_tiploc_only(self):
        params = create_parameters("KNGX")
        assert params["code"] == "gb-nr:KNGX"
        assert "  " not in params["timeFrom"]
        assert "  " not in params["timeTo"]
        # Must parse as valid single-space datetime
        dt.datetime.strptime(params["timeFrom"], "%Y-%m-%d %H%M")
        dt.datetime.strptime(params["timeTo"], "%Y-%m-%d %H%M")

    def test_date_and_time_no_double_space(self):
        params = create_parameters("KNGX", date_from="2026-05-20", time_from="1000")
        assert params["timeFrom"] == "2026-05-20 1000"
        assert params["timeTo"] == "2026-05-20 1400"
        assert "  " not in params["timeFrom"]

    def test_formatted_time_input(self):
        params = create_parameters("KNGX", date_from="2026-05-20", time_from="10:30")
        assert params["timeFrom"] == "2026-05-20 1030"

    def test_date_only_defaults_full_day(self):
        params = create_parameters("KNGX", date_from="2026-05-20")
        assert params["timeFrom"] == "2026-05-20 0000"
        assert params["timeTo"] == "2026-05-20 2359"

    def test_explicit_time_range(self):
        params = create_parameters(
            "KNGX",
            date_from="2026-05-20",
            time_from="1000",
            time_to="1600",
        )
        assert params["timeFrom"] == "2026-05-20 1000"
        assert params["timeTo"] == "2026-05-20 1600"

    def test_filter_stations(self):
        params = create_parameters("KNGX", filter_from="STEVNGE", filter_to="PBRO")
        assert params["filterFrom"] == "gb-nr:STEVNGE"
        assert params["filterTo"] == "gb-nr:PBRO"

    def test_invalid_date_format_raises(self):
        with pytest.raises(InvalidDateProvided):
            create_parameters("KNGX", date_from="2026/05/20")

    def test_invalid_time_format_raises(self):
        with pytest.raises(InvalidTimeProvided):
            create_parameters("KNGX", time_from="25:99")

    def test_invalid_tiploc_length_raises(self):
        with pytest.raises(InvalidTIPLOCProvided):
            create_parameters("K")
        with pytest.raises(InvalidTIPLOCProvided):
            create_parameters("TOOLONGSTATION")
