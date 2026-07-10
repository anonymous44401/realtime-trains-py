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


class InvalidDateProvided(Exception):
    def __init__(self, invalid_item: str) -> None:
        super().__init__(
            f'\nrealtime-trains-py error:\nThe date you provided didn\'t meet the requirements or fall into a valid range. \nGiven: "{invalid_item}" \nExpected: YYYY-MM-DD format (like "2026-02-26").'
        )


class InvalidTimeProvided(Exception):
    def __init__(self, invalid_item: str) -> None:
        super().__init__(
            f'\nrealtime-trains-py error:\nThe time you provided didn\'t meet the requirements or fall into a valid range. \nGiven: "{invalid_item}" \nExpected: HHMM format (like "1800").'
        )


class InvalidTIPLOCProvided(Exception):
    def __init__(self, invalid_item: str) -> None:
        super().__init__(
            f'\nrealtime-trains-py error:\nThe TIPLOC you provided didn\'t meet the requirements or fall into a valid range. \nGiven: "{invalid_item}" \nExpected: A string with length 4-7 characters (like "KNGX" or "CLPHMJN").'
        )


class InvalidUIDProvided(Exception):
    def __init__(self, invalid_item: str) -> None:
        super().__init__(
            f'\nrealtime-trains-py error:\nThe Service UID you provided didn\'t meet the requirements or fall into a valid range. \nGiven: "{invalid_item}" \nExpected: A string with 5 digits (starting with a capital letter in some cases) (like "A12345" or "12345").'
        )


class NoDataFound(Exception):
    def __init__(self) -> None:
        super().__init__(
            "\nrealtime-trains-py error:\nNo data found for the request made. Please check your parameters and try again."
        )
