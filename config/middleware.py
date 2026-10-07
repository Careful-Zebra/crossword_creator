# config/middleware.py

PORTFOLIO = "https://main.d27pshxw3r4sn9.amplifyapp.com"

class FrameAncestorsMiddleware:
    """
    Allow the portfolio to iframe the PUBLIC crossword pages, but never /admin/.
    X-Frame-Options can't whitelist an external origin, so strip it on public
    pages and let a CSP frame-ancestors (self + portfolio) govern framing instead.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not request.path.startswith("/admin/"):
            response["Content-Security-Policy"] = f"frame-ancestors 'self' {PORTFOLIO}"
            if response.has_header("X-Frame-Options"):
                del response["X-Frame-Options"]
        return response
