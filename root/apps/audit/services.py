from .models import AuditLog

def log_audit(
    *,
    organization,
    actor,
    action,
    message,
    object_type=None,
    object_id=None,
    metadata=None
):
    AuditLog.objects.create(
        organization=organization,
        actor=actor,
        action=action,
        message=message,
        object_type=object_type,
        object_id=object_id,
        metadata=metadata or {}
    )
