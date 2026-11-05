"""Shared API error types."""


class ApiError(Exception):
    status = 400

    def __init__(self, message, status=None):
        super().__init__(message)
        self.message = message
        if status is not None:
            self.status = status


class Conflict(ApiError):
    status = 409


class Unauthorized(ApiError):
    status = 401


class Forbidden(ApiError):
    status = 403


class NotFound(ApiError):
    status = 404


def as_response(err):
    return {"error": err.message}, err.status
