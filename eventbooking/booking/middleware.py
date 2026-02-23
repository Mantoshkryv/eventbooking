import time
from django.http import JsonResponse

ip_requests = {}
blocked_ip = {}

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get("REMOTE_ADDR")
        now = time.time()

        if ip in blocked_ip and now < blocked_ip[ip]:
            return JsonResponse({"error": "Blocked for 1 minute"}, status=429)

        ip_requests.setdefault(ip, [])
        ip_requests[ip] = [t for t in ip_requests[ip] if now - t < 60]

        if len(ip_requests[ip]) >= 10:
            blocked_ip[ip] = now + 60
            return JsonResponse({"error": "Too many requests"}, status=429)

        ip_requests[ip].append(now)
        return self.get_response(request)