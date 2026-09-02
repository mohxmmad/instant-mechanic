import logging
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        # Log 4xx/5xx
        request = context.get("request")
        path = request.path if request else "unknown"
        if response.status_code >= 500:
            logger.error("Server error at %s: %s", path, exc, exc_info=True)
        elif response.status_code >= 400:
            logger.warning("Client error %s at %s: %s", response.status_code, path, response.data)
        # Do NOT expose traceback - DRF already hides it
    else:
        # Unhandled exception
        logger.error("Unhandled exception: %s", exc, exc_info=True)
    return response
