from realtime_trains_py.internal.details import LocationData, ServiceData
from realtime_trains_py.internal.utilities import fmt
from realtime_trains_py.parsing.parse_service_board import (
    arrange_output,
    calling_point_line,
    final_calling_point,
)


def sample_service(platform_intermediate="3", platform_final=""):
    calling_points = [
        LocationData(
            stop_name="Stevenage",
            scheduled_arrival="",
            expected_arrival="",
            platform=platform_intermediate,
            line="",
            scheduled_departure="10:30",
            expected_departure="On time",
            scheduled_pass="",
            expected_pass="",
            coaches=6,
            terminus="",
            origin="",
            service_uid="G12345",
        ),
        LocationData(
            stop_name="Peterborough",
            scheduled_arrival="11:00",
            expected_arrival="On time",
            platform=platform_final,
            line="",
            scheduled_departure="",
            expected_departure="",
            scheduled_pass="",
            expected_pass="",
            coaches=6,
            terminus="",
            origin="",
            service_uid="G12345",
        ),
    ]

    return ServiceData(
        service_uid="G12345",
        operator="LNER",
        origin="London Kings Cross",
        destination="Peterborough",
        calling_points=calling_points,
        start_time="10:00",
        end_time="11:00",
        coaches=6,
    )


class TestArrangeOutput:
    def test_global_fmt_not_mutated(self):
        orig_white = fmt["white"]
        orig_green = fmt["green"]
        orig_blue = fmt["blue"]

        service = sample_service()
        # Format in yellow DMI mode
        output = arrange_output(service, mode="DMI.Y")

        assert "\033[1;33m" in output  # Yellow should be present
        # Global dictionary must remain untouched
        assert fmt["white"] == orig_white
        assert fmt["green"] == orig_green
        assert fmt["blue"] == orig_blue

    def test_platform_descriptor_rendered_when_present(self):
        service = sample_service(platform_intermediate="3", platform_final="2")
        output = arrange_output(service, mode="LCD")

        assert "P3" in output
        assert "P2" in output

    def test_platform_descriptor_omitted_when_blank(self):
        # Regression test for watch_service showing platform descriptor when no platform was given
        service = sample_service(platform_intermediate="", platform_final="")
        output = arrange_output(service, mode="LCD")

        assert "P" not in output or "P3" not in output
        # Specifically verify lines don't contain dangling 'P ' or 'P \n'
        for line in output.splitlines():
            if "Stevenage" in line:
                assert " P " not in line and " P\n" not in line
            if "Peterborough" in line:
                assert " P " not in line and " P\n" not in line


class TestCallingPointFormatting:
    def test_calling_point_line_with_platform(self):
        res = calling_point_line(
            exp_dep="On time",
            sch_dep="10:30",
            stop="Stevenage",
            platform="4B",
        )
        assert "P4B" in res

    def test_calling_point_line_without_platform(self):
        res = calling_point_line(
            exp_dep="On time",
            sch_dep="10:30",
            stop="Stevenage",
            platform="",
        )
        assert " P" not in res

    def test_final_calling_point_with_platform(self):
        res = final_calling_point(
            exp_arr="On time",
            sch_arr="11:00",
            stop="Peterborough",
            platform="1",
        )
        assert "P1" in res

    def test_final_calling_point_without_platform(self):
        res = final_calling_point(
            exp_arr="On time",
            sch_arr="11:00",
            stop="Stevenage",
            platform="",
        )
        assert " P" not in res
