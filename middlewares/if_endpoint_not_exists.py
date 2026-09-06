from typing import Callable, Awaitable

from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

EXCLUDED_ENDPOINTS = {'api/answer_evaluate', 'api/check_solution'}

class IfEndpointNotExists(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        response = await call_next(request)

        if response.status_code == 404 and not any([endpoint in str(request.url) for endpoint in EXCLUDED_ENDPOINTS]):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    'status': False,
                    'err_description': 'The endpoint doesn\'t exist'
                }
            )

        return response
