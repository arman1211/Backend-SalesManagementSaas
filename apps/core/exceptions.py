from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_payload = {
            "success": False,
            "status_code": response.status_code,
            "errors": response.data,
        }
        response.data = error_payload

    return response
