# todo_app/middleware.py
class CsrfExemptForHtmx:
    """
    Middleware to exempt CSRF for HTMX requests if needed.
    Alternatively, ensure CSRF tokens are properly included in templates.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip CSRF for HTMX delete if still having issues
        if request.htmx and request.method == 'POST':
            setattr(request, '_dont_enforce_csrf_checks', True)
        return self.get_response(request)