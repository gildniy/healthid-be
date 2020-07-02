import json
from django.utils.deprecation import MiddlewareMixin


class IgnoreToken(MiddlewareMixin):
    def process_request(self, request):
        try:
            if request.method == 'POST':
                query = ''
                body = json.loads(request.body)
                for line in (body.get('query') or '').split('\n'):
                    if '#' not in line:
                        query += line
                if 'mutation' in query and 'loginUser' in query:
                    del request.META['HTTP_AUTHORIZATION']
        except Exception:
            pass
