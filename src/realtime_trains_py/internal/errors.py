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
            f'\nrealtime-trains-py error:\nThe date you provided didn\'t meet the requirements or fall into a valid range. \nGiven: "{invalid_item}" \nExpected: YYYY-MM-DD format.'
        )


class InvalidTimeProvided(Exception):
    def __init__(self, invalid_item: str) -> None:
        super().__init__(
            f'\nrealtime-trains-py error:\nThe time you provided didn\'t meet the requirements or fall into a valid range. \nGiven: "{invalid_item}" \nExpected: HHMM format.'
        )


class InvalidUIDProvided(Exception):
    def __init__(self, invalid_item: str) -> None:
        super().__init__(
            f'\nrealtime-trains-py error:\nThe Service UID you provided didn\'t meet the requirements or fall into a valid range. \nGiven: "{invalid_item}" \nExpected: A string starting with a capital letter followed by 5 digits (e.g., A12345).'
        )


class NoDataFound(Exception):
    def __init__(self) -> None:
        super().__init__(
            "\nrealtime-trains-py error:\nNo data found for the request made. Please check your parameters and try again."
        )
