"""
UTF-8 Encoding Middleware for Nawab Urdu Academy
Ensures all responses use proper UTF-8 encoding
"""


def utf8_encoding_middleware(get_response):
    """
    Middleware to ensure UTF-8 encoding on all HTTP responses.
    Prevents double encoding issues with Urdu text.
    """
    def middleware(request):
        response = get_response(request)
        
        # Set charset to UTF-8 for text responses
        content_type = response.get('Content-Type', '')
        if content_type.startswith('text/') or 'application/json' in content_type:
            if 'charset' not in content_type.lower():
                if 'application/json' in content_type:
                    response['Content-Type'] = 'application/json; charset=utf-8'
                elif 'text/html' in content_type:
                    response['Content-Type'] = 'text/html; charset=utf-8'
                elif 'text/plain' in content_type:
                    response['Content-Type'] = 'text/plain; charset=utf-8'
                elif 'text/css' in content_type:
                    response['Content-Type'] = 'text/css; charset=utf-8'
                elif 'javascript' in content_type:
                    response['Content-Type'] = 'application/javascript; charset=utf-8'
        
        return response
    
    return middleware