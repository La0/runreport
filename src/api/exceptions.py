from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError


def runreport_exception_handler(exc, context):
    '''
    Cleanup DRF validation errors to simplify output
    '''
    response = exception_handler(exc, context)
    if response is not None:
        if isinstance(exc, ValidationError):
            details = exc.get_full_details()

            # Rename non_field_errors
            if 'non_field_errors' in details:
                details['global'] = details['non_field_errors']
                del details['non_field_errors']

            # Simplify exception structure
            response.data = {
                name: {
                    err['code']: err['message']
                    for err in errors
                }
                for name, errors in details.items()
            }

    return response
