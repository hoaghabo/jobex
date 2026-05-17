from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    """
    - Read برای همه
    - Write فقط برای ادمین
    """

    def has_permission(self, request, view):
        # GET, HEAD, OPTIONS
        if request.method in SAFE_METHODS:
            return True
        
        # POST, PUT, PATCH, DELETE
        return request.user and request.user.is_staff
