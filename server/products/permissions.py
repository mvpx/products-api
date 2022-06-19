from rest_framework import permissions


class CustomPermission(permissions.BasePermission):

    methods = ("GET",)

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        if request.method in self.methods:
            return True
        return False
