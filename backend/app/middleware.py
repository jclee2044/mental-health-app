"""Transport policy only: personal API responses must not be cached."""
class NoStoreMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        async def send_with_policy(message):
            if message["type"] == "http.response.start" and scope.get("path", "").startswith("/api"):
                headers = [(key, value) for key, value in message.get("headers", []) if key.lower() != b"cache-control"]
                message = {**message, "headers": [*headers, (b"cache-control", b"no-store")]}
            await send(message)
        await self.app(scope, receive, send_with_policy)
