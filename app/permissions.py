from rest_framework.permissions import BasePermission
from django.utils import timezone
from datetime import timedelta


class CanUpdateWithin4Hours(BasePermission):
    message = "You can update this object only within 4 hours of creation."

    def has_object_permission(self, request, view, obj):
        if request.method not in ['PUT', 'PATCH']:
            return True
        
        if obj.owner != request.user:
            return False
        
        time_limit = obj.created_at + timedelta(hours=4)
        return timezone.now() <= time_limit
