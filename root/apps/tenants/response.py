from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
import uuid

def success_response(data=None, message="Success", status_code=status.HTTP_200_OK, request=None):
    return Response(
        {
            "message": message,
            "meta": data if data else {},
            "error": None,
            "status_code": status_code,
            "success": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": str(uuid.uuid4()),
            "path": request.path if request else None,
            "method": request.method if request else None,
            "version": "v1"
        },
        status=status_code
    )


def error_response(errors=None, message="Error", status_code=status.HTTP_400_BAD_REQUEST, request=None):
    return Response(
        {
            "message": message,
            "meta": {},
            "error": errors,
            "status_code": status_code,
            "success": False,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": str(uuid.uuid4()),
            "path": request.path if request else None,
            "method": request.method if request else None,
            "version": "v1"
        },
        status=status_code
    )
