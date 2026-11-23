from unittest.mock import MagicMock, patch

import pytest
import requests

from realtime_trains_py import (
    HTTPConnectionError,
    HTTPTimeoutError,
    HTTPTransportError,
    RealtimeTrainsPy,
)
from realtime_trains_py.internal.requests import (
    DEFAULT_TIMEOUT,
    HTTPTransport,
    get_request,
    update_headers,
)


class TestHTTPTransportBasics:
    def test_successful_get_request(self):
        mock_session = MagicMock(spec=requests.Session)
        mock_response = MagicMock(status_code=200)
        mock_session.request.return_value = mock_response

        transport = HTTPTransport(session=mock_session)
        resp = transport.get("api/info")

        assert resp == mock_response
        mock_session.request.assert_called_once_with(
            method="GET",
            url="https://data.rtt.io/api/info",
            headers=None,
            params=None,
            timeout=DEFAULT_TIMEOUT,
        )

    def test_method_normalization(self):
        mock_session = MagicMock(spec=requests.Session)
        transport = HTTPTransport(session=mock_session)

        transport.request("post", "api/endpoint")
        mock_session.request.assert_called_once_with(
            method="POST",
            url="https://data.rtt.io/api/endpoint",
            headers=None,
            params=None,
            timeout=DEFAULT_TIMEOUT,
        )

    def test_url_composition(self):
        mock_session = MagicMock(spec=requests.Session)
        transport = HTTPTransport(session=mock_session)

        # Leading slash stripped cleanly
        transport.get("/rtt/location")
        assert (
            mock_session.request.call_args.kwargs["url"]
            == "https://data.rtt.io/rtt/location"
        )

        # Fully-qualified HTTP/HTTPS URLs left intact
        transport.get("https://custom.host/custom/path")
        assert (
            mock_session.request.call_args.kwargs["url"]
            == "https://custom.host/custom/path"
        )

        transport.get("http://custom.host/insecure")
        assert (
            mock_session.request.call_args.kwargs["url"]
            == "http://custom.host/insecure"
        )

        # Surrounding whitespace is stripped cleanly
        transport.get("  api/info  ")
        assert (
            mock_session.request.call_args.kwargs["url"]
            == "https://data.rtt.io/api/info"
        )

    def test_header_and_params_forwarding(self):
        mock_session = MagicMock(spec=requests.Session)
        transport = HTTPTransport(session=mock_session)

        headers = {"Authorization": "Bearer token123", "Accept": "application/json"}
        params = {"code": "gb-nr:KNGX", "detailed": "true"}

        transport.get("rtt/location", headers=headers, params=params)

        mock_session.request.assert_called_once_with(
            method="GET",
            url="https://data.rtt.io/rtt/location",
            headers=headers,
            params=params,
            timeout=DEFAULT_TIMEOUT,
        )


class TestHTTPTransportTimeouts:
    def test_default_timeout_used(self):
        mock_session = MagicMock(spec=requests.Session)
        transport = HTTPTransport(session=mock_session)

        transport.get("api/info")
        assert mock_session.request.call_args.kwargs["timeout"] == DEFAULT_TIMEOUT

    def test_per_request_timeout_override(self):
        mock_session = MagicMock(spec=requests.Session)
        transport = HTTPTransport(session=mock_session)

        transport.get("api/info", timeout=5.0)
        assert mock_session.request.call_args.kwargs["timeout"] == 5.0

    def test_tuple_timeout_support(self):
        mock_session = MagicMock(spec=requests.Session)
        transport = HTTPTransport(session=mock_session)

        transport.get("api/info", timeout=(3.0, 10.0))
        assert mock_session.request.call_args.kwargs["timeout"] == (3.0, 10.0)


class TestHTTPTransportExceptionHandling:
    def test_connection_error_translation_and_chaining(self):
        mock_session = MagicMock(spec=requests.Session)
        original_exc = requests.exceptions.ConnectionError("Failed to resolve host")
        mock_session.request.side_effect = original_exc

        transport = HTTPTransport(session=mock_session)

        with pytest.raises(HTTPConnectionError) as exc_info:
            transport.get("api/info")

        assert isinstance(exc_info.value, HTTPTransportError)
        assert exc_info.value.__cause__ is original_exc
        assert "Failed to connect to the RTT API server" in str(exc_info.value)

    def test_timeout_error_translation_and_chaining(self):
        mock_session = MagicMock(spec=requests.Session)
        original_exc = requests.exceptions.ReadTimeout(
            "Read timed out after 10 seconds"
        )
        mock_session.request.side_effect = original_exc

        transport = HTTPTransport(session=mock_session)

        with pytest.raises(HTTPTimeoutError) as exc_info:
            transport.get("api/info")

        assert isinstance(exc_info.value, HTTPTransportError)
        assert exc_info.value.__cause__ is original_exc
        assert "Request to the RTT API timed out" in str(exc_info.value)

    def test_general_request_exception_translation_and_chaining(self):
        mock_session = MagicMock(spec=requests.Session)
        original_exc = requests.exceptions.TooManyRedirects("Exceeded 30 redirects")
        mock_session.request.side_effect = original_exc

        transport = HTTPTransport(session=mock_session)

        with pytest.raises(HTTPTransportError) as exc_info:
            transport.get("api/info")

        assert exc_info.value.__cause__ is original_exc
        assert "HTTP transport error" in str(exc_info.value)


class TestHTTPTransportLifecycle:
    def test_session_reuse_across_requests(self):
        with HTTPTransport() as transport:
            session_instance = transport.session
            assert isinstance(session_instance, requests.Session)

            with patch.object(session_instance, "request") as mock_req:
                mock_req.return_value = MagicMock(status_code=200)

                transport.get("api/info")
                transport.get("rtt/location")

                assert mock_req.call_count == 2
                assert transport.session is session_instance

    def test_close_owned_session(self):
        mock_session = MagicMock(spec=requests.Session)
        with patch(
            "realtime_trains_py.internal.requests.requests.Session",
            return_value=mock_session,
        ):
            transport = HTTPTransport()
            assert not transport.is_closed

            transport.close()
            assert transport.is_closed
            mock_session.close.assert_called_once()

            # Second close call is idempotent
            transport.close()
            assert mock_session.close.call_count == 1

    def test_external_session_not_closed_by_transport(self):
        mock_session = MagicMock(spec=requests.Session)
        transport = HTTPTransport(session=mock_session)

        transport.close()
        assert transport.is_closed
        mock_session.close.assert_not_called()

    def test_request_on_closed_transport_raises(self):
        transport = HTTPTransport()
        transport.close()

        with pytest.raises(
            HTTPTransportError, match="Cannot make requests on a closed HTTP transport"
        ):
            transport.get("api/info")

    def test_context_manager_lifecycle(self):
        mock_session = MagicMock(spec=requests.Session)
        with patch(
            "realtime_trains_py.internal.requests.requests.Session",
            return_value=mock_session,
        ):
            with HTTPTransport() as transport:
                assert not transport.is_closed

            assert transport.is_closed
            mock_session.close.assert_called_once()

    def test_entering_closed_transport_raises(self):
        transport = HTTPTransport()
        transport.close()

        with pytest.raises(
            HTTPTransportError, match="Cannot enter a closed HTTP transport"
        ):
            with transport:
                pass

    def test_close_guarantees_closed_flag_even_on_session_error(self):
        mock_session = MagicMock(spec=requests.Session)
        mock_session.close.side_effect = RuntimeError("Socket cleanup error")

        with patch(
            "realtime_trains_py.internal.requests.requests.Session",
            return_value=mock_session,
        ):
            transport = HTTPTransport()
            with pytest.raises(RuntimeError, match="Socket cleanup error"):
                transport.close()

            assert transport.is_closed is True


class TestRealtimeTrainsPyTransportIntegration:
    def test_session_reuse_across_api_methods(self):
        mock_session = MagicMock(spec=requests.Session)
        auth_resp = MagicMock(status_code=200)
        data_resp = MagicMock(status_code=200)
        data_resp.json.return_value = {"locations": []}
        mock_session.request.side_effect = [auth_resp, data_resp, data_resp]

        with patch(
            "realtime_trains_py.internal.requests.requests.Session",
            return_value=mock_session,
        ):
            with RealtimeTrainsPy(request_token="dummy") as rtt:
                rtt.lookup(raw=True)
                rtt.lookup(raw=True)

        assert mock_session.request.call_count == 3

    def test_close_and_context_manager(self):
        mock_session = MagicMock(spec=requests.Session)
        mock_session.request.return_value = MagicMock(status_code=200)
        with patch(
            "realtime_trains_py.internal.requests.requests.Session",
            return_value=mock_session,
        ):
            with RealtimeTrainsPy(request_token="dummy") as rtt:
                assert not rtt._RealtimeTrainsPy__transport.is_closed

            assert rtt._RealtimeTrainsPy__transport.is_closed

    def test_client_requests_use_default_timeout(self):
        mock_session = MagicMock(spec=requests.Session)
        auth_resp = MagicMock(status_code=200)
        dept_resp = MagicMock(status_code=200)
        dept_resp.json.return_value = {"services": []}
        mock_session.request.side_effect = [auth_resp, dept_resp]

        with patch(
            "realtime_trains_py.internal.requests.requests.Session",
            return_value=mock_session,
        ):
            with RealtimeTrainsPy(request_token="dummy") as rtt:
                rtt.get_departures("KNGX", raw=True)

        assert mock_session.request.call_args.kwargs["timeout"] == DEFAULT_TIMEOUT

    def test_get_departures_and_service_use_transport(self):
        mock_session = MagicMock(spec=requests.Session)
        auth_resp = MagicMock(status_code=200)
        dept_resp = MagicMock(status_code=200)
        dept_resp.json.return_value = {"services": []}
        service_resp = MagicMock(status_code=200)
        service_resp.json.return_value = {"service": {}}
        mock_session.request.side_effect = [auth_resp, dept_resp, service_resp]

        with patch(
            "realtime_trains_py.internal.requests.requests.Session",
            return_value=mock_session,
        ):
            with RealtimeTrainsPy(request_token="dummy") as rtt:
                rtt.get_departures("KNGX", raw=True)
                rtt.get_service("G12345", raw=True)

        assert mock_session.request.call_count == 3
        calls = mock_session.request.call_args_list
        assert calls[0].kwargs["url"] == "https://data.rtt.io/api/info"
        assert calls[1].kwargs["url"] == "https://data.rtt.io/rtt/location"
        assert calls[2].kwargs["url"] == "https://data.rtt.io/rtt/service"

    def test_401_retry_uses_transport(self):
        tokens_issued = ["tok1", "tok2"]
        location_auth_headers = []

        def mock_request(method, url, headers=None, params=None, timeout=None):
            if "api/info" in url:
                return MagicMock(status_code=401)
            if "api/get_access_token" in url:
                tok = tokens_issued.pop(0) if tokens_issued else "tok2"
                resp = MagicMock(status_code=200)
                resp.json.return_value = {
                    "token": tok,
                    "validUntil": "2026-11-25T14:00:00Z",
                }
                return resp
            if "rtt/location" in url:
                if headers:
                    location_auth_headers.append(headers.get("Authorization"))
                if headers and headers.get("Authorization") == "Bearer tok1":
                    return MagicMock(status_code=401)
                resp = MagicMock(status_code=200)
                resp.json.return_value = {"services": []}
                return resp
            return MagicMock(status_code=200)

        mock_session = MagicMock(spec=requests.Session)
        mock_session.request.side_effect = mock_request

        with patch(
            "realtime_trains_py.internal.requests.requests.Session",
            return_value=mock_session,
        ):
            with RealtimeTrainsPy(request_token="dummy") as rtt:
                res = rtt.get_departures("KNGX", raw=True)
                assert res == {"services": []}

        # Verify retry occurred through the same transport with renewed bearer token
        assert location_auth_headers == ["Bearer tok1", "Bearer tok2"]

    def test_transport_timeout_bubbles_up(self):
        mock_session = MagicMock(spec=requests.Session)
        auth_resp = MagicMock(status_code=200)
        timeout_exc = requests.exceptions.ConnectTimeout("Timed out connecting")
        mock_session.request.side_effect = [auth_resp, timeout_exc]

        with patch(
            "realtime_trains_py.internal.requests.requests.Session",
            return_value=mock_session,
        ):
            with RealtimeTrainsPy(request_token="dummy") as rtt:
                with pytest.raises(HTTPTimeoutError):
                    rtt.get_departures("KNGX")

    def test_entering_closed_client_raises(self):
        mock_session = MagicMock(spec=requests.Session)
        mock_session.request.return_value = MagicMock(status_code=200)
        with patch(
            "realtime_trains_py.internal.requests.requests.Session",
            return_value=mock_session,
        ):
            rtt = RealtimeTrainsPy(request_token="dummy")
            rtt.close()

            with pytest.raises(
                HTTPTransportError,
                match="Cannot enter a closed RealtimeTrainsPy client",
            ):
                with rtt:
                    pass

    def test_401_retry_updates_shared_headers_in_place(self):
        tokens_issued = ["tok1", "tok2"]

        def mock_request(method, url, headers=None, params=None, timeout=None):
            if "api/info" in url:
                return MagicMock(status_code=401)
            if "api/get_access_token" in url:
                tok = tokens_issued.pop(0) if tokens_issued else "tok2"
                resp = MagicMock(status_code=200)
                resp.json.return_value = {
                    "token": tok,
                    "validUntil": "2026-11-25T14:00:00Z",
                }
                return resp
            if "rtt/location" in url:
                if headers and headers.get("Authorization") == "Bearer tok1":
                    return MagicMock(status_code=401)
                resp = MagicMock(status_code=200)
                resp.json.return_value = {"services": []}
                return resp
            return MagicMock(status_code=200)

        mock_session = MagicMock(spec=requests.Session)
        mock_session.request.side_effect = mock_request

        with patch(
            "realtime_trains_py.internal.requests.requests.Session",
            return_value=mock_session,
        ):
            with RealtimeTrainsPy(request_token="dummy") as rtt:
                headers_ref = rtt._RealtimeTrainsPy__headers
                assert headers_ref["Authorization"] == "Bearer tok1"

                rtt.get_departures("KNGX", raw=True)

                # Header dictionary must be mutated in-place to maintain reference identity
                assert rtt._RealtimeTrainsPy__headers is headers_ref
                assert headers_ref["Authorization"] == "Bearer tok2"


class TestUpdateHeadersHelper:
    def test_update_headers_delegates_to_transport(self):
        mock_transport = MagicMock(spec=HTTPTransport)
        info_resp = MagicMock(status_code=200)
        mock_transport.get.return_value = info_resp

        headers = update_headers("dummy_token", transport=mock_transport)

        mock_transport.get.assert_called_once_with(
            "api/info",
            headers={
                "Accept": "application/json",
                "Authorization": "Bearer dummy_token",
            },
        )
        assert headers == {
            "Accept": "application/json",
            "Authorization": "Bearer dummy_token",
        }


class TestGetRequestHelper:
    def test_get_request_delegates_to_transport(self):
        mock_transport = MagicMock(spec=HTTPTransport)
        mock_response = MagicMock(status_code=200)
        mock_transport.get.return_value = mock_response

        resp = get_request(
            endpoint="api/info",
            headers={"Accept": "application/json"},
            params={"k": "v"},
            timeout=5,
            transport=mock_transport,
        )

        assert resp == mock_response
        mock_transport.get.assert_called_once_with(
            "api/info",
            headers={"Accept": "application/json"},
            params={"k": "v"},
            timeout=5,
        )

    @patch("realtime_trains_py.internal.requests.get")
    def test_standalone_get_request_translates_timeout(self, mock_get):
        original_exc = requests.exceptions.Timeout("Connection timed out")
        mock_get.side_effect = original_exc

        with pytest.raises(HTTPTimeoutError) as exc_info:
            get_request("api/info", headers={"Accept": "application/json"})

        assert exc_info.value.__cause__ is original_exc

    @patch("realtime_trains_py.internal.requests.get")
    def test_standalone_get_request_translates_connection_error(self, mock_get):
        original_exc = requests.exceptions.ConnectionError("Connection refused")
        mock_get.side_effect = original_exc

        with pytest.raises(HTTPConnectionError) as exc_info:
            get_request("api/info", headers={"Accept": "application/json"})

        assert exc_info.value.__cause__ is original_exc
