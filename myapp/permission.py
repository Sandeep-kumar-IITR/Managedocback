from rest_framework.permissions import BasePermission
from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Doc
from .models import ChatMessage


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return Doc.objects.filter(user=request.user).exists()



class IsOwnerdelete(BasePermission):
    """
    Allow actions only if the object belongs to the user.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user




class IsOwnerupdate(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user




class IsOwnerchatlist(BasePermission):
    def has_permission(self, request, view):
        return ChatMessage.objects.filter(user=request.user).exists()
