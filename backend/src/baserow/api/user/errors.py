from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT
from django.conf import settings

# None of these are passwords
ERROR_ALREADY_EXISTS = "ERROR_EMAIL_ALREADY_EXISTS"  # nosec
ERROR_USER_NOT_FOUND = "ERROR_USER_NOT_FOUND"  # nosec
ERROR_INVALID_OLD_PASSWORD = "ERROR_INVALID_OLD_PASSWORD"  # nosec
ERROR_INVALID_PASSWORD = "ERROR_INVALID_PASSWORD"  # nosec
ERROR_USER_IS_LAST_ADMIN = "ERROR_USER_IS_LAST_ADMIN"
ERROR_DISABLED_SIGNUP = "ERROR_DISABLED_SIGNUP"  # nosec
ERROR_CLIENT_SESSION_ID_HEADER_NOT_SET = (
    "ERROR_CLIENT_SESSION_ID_HEADER_NOT_SET",
    HTTP_400_BAD_REQUEST,
    f"The {settings.CLIENT_SESSION_ID_HEADER} must be set when using this endpoint.",
)
ERROR_DISABLED_RESET_PASSWORD = "ERROR_DISABLED_RESET_PASSWORD"  # nosec

ERROR_UNDO_REDO_LOCK_CONFLICT = (
    "ERROR_UNDO_REDO_LOCK_CONFLICT",
    HTTP_409_CONFLICT,
    "An operation is running in the background or triggered by another user preventing "
    "your undo/redo action. Please wait until the other operation finishes.",
)
