import sys


class SilentException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class InternalError(SilentException):
    def __init__(self, message: str):
        super().__init__(f"Internal Error: {message}")


class ModuleError(SilentException):
    def __init__(self, message: str):
        super().__init__(f"Module Error: {message}")


class UsageError(SilentException):
    def __init__(self, message: str):
        super().__init__(f"Usage: fluffpkg {message}")


class AlreadyInstalled(SilentException):
    def __init__(self, package: str):
        super().__init__(f"Package '{package}' is already installed")


class AlreadyNewest(SilentException):
    def __init__(self, package: str):
        super().__init__(f"Package '{package}' is already newest")


class NoCandidate(SilentException):
    def __init__(self):
        super().__init__("No sources found")


class MultipleCandidates(SilentException):
    def __init__(self):
        super().__init__("Multiple candidates found")


class SpecificVersion(SilentException):
    def __init__(self):
        super().__init__(
            "This package is was installed as a specific version. Use --force to override"
        )


class APICallFailed(SilentException):
    def __init__(self, message: str):
        super().__init__(message)


### SourcesLib


class AlreadySourced(SilentException):
    def __init__(self, package: str):
        super().__init__(f"Package '{package}' is already sourced")


class SourceNotFound(SilentException):
    def __init__(self, source: str):
        super().__init__(f"Source '{source}' not found")


class SourceAlreadyExists(SilentException):
    def __init__(self):
        super().__init__("This source is already included. Please update it instead")


### ArgumentLib
class UnknownCommand(SilentException):
    def __init__(self, command: str):
        super().__init__(f"Unknown Command: {command}")


# Custom exception hook
def handle_uncaught(exc_type, exc_value, traceback):
    if isinstance(exc_value, SilentException):
        print(exc_value.message)
        sys.exit(1)
    else:
        # Default behavior for other exceptions
        sys.__excepthook__(exc_type, exc_value, traceback)


# Set the global exception hook
sys.excepthook = handle_uncaught
