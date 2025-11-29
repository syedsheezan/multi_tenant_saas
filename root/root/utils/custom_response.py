from rest_framework.response import Response
from datetime import datetime
import uuid

def custom_response(message, data=None, status_code=200, request=None, error=None):
    response_data = {
        "message": message,
        "meta": data if data else {},
        "error": error,
        "status_code": status_code,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "request_id": str(uuid.uuid4()),
        "path": request.path if request else None,
        "method": request.method if request else None,
        "version": "v1"
    }
    return Response(response_data, status=status_code)
