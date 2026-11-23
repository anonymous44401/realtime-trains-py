# Custom exception classes for realtime-trains-py


class APIResponseError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(
            f"\nrealtime-trains-py error:\nAPI response error: \n{message}"
        )


class AuthenticationError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(
            f"\nrealtime-trains-py error:\nAPI authentication failed. Check your credentials and try again. \n{message}"
        )


class FileWriteError(Exception):
    def __init__(self, file: str) -> None:
        super().__init__(
            f'\nrealtime-trains-py error:\nFailed to write to file. Perhaps the file already exists? \nFile: "{file}"'
        )


class HTTPTransportError(Exception):
    def __init__(self, message: str, prefix: str = "HTTP transport error") -> None:
        self.message = message
        super().__init__(f"\nrealtime-trains-py error:\n{prefix}: \n{message}")


class HTTPConnectionError(HTTPTransportError):
    def __init__(self, message: str) -> None:
        super().__init__(message, prefix="Failed to connect to the RTT API server")


class HTTPTimeoutError(HTTPTransportError):
    def __init__(self, message: str) -> None:
        super().__init__(message, prefix="Request to the RTT API timed out")


class InvalidDateProvided(Exception):
    def __init__(self, invalid_item: str) -> None:
        super().__init__(
            f'\nrealtime-trains-py error:\nThe date you provided didn\'t meet the requirements or fall into a valid range. \nGiven: "{invalid_item}" \nExpected: YYYY-MM-DD format (like "2026-02-26").'
        )


class InvalidTimeProvided(Exception):
    def __init__(self, invalid_item: str) -> None:
        super().__init__(
            f'\nrealtime-trains-py error:\nThe time you provided didn\'t meet the requirements or fall into a valid range. \nGiven: "{invalid_item}" \nExpected: HHMM or HH:MM format (like "1800" or "18:00").'
        )


class InvalidTIPLOCProvided(Exception):
    def __init__(self, invalid_item: str) -> None:
        super().__init__(
            f'\nrealtime-trains-py error:\nThe TIPLOC you provided didn\'t meet the requirements or fall into a valid range. \nGiven: "{invalid_item}" \nExpected: A string with length 3-7 characters (like "SVG", "KNGX" or "CLPHMJN"). \nUse the lookup feature to find TIPLOCs'
        )


class InvalidUIDProvided(Exception):
    def __init__(self, invalid_item: str) -> None:
        super().__init__(
            f'\nrealtime-trains-py error:\nThe Service UID you provided didn\'t meet the requirements or fall into a valid range. \nGiven: "{invalid_item}" \nExpected: A string with 5 digits (and starting with a capital letter in some cases) (like "A12345" or "12345").'
        )


class NoDataFound(Exception):
    def __init__(self) -> None:
        super().__init__(
            "\nrealtime-trains-py error:\nNo data found for the request made. Please check your parameters and try again."
        )
