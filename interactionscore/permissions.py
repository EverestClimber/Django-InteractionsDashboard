# from rest_framework import permissions
#
#
# class OwnsIt(permissions.BasePermission):
#
#     def has_object_permission(self, request, view, obj):
#         # users with access to dj-admin are always allowed
#         if request.user.is_staff:
#             return True
#         # require presence of an owner, and that owner being current user
#         return obj.user and request.user.id == obj.user.id
#
#
# class CanApproveOwn(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         # users with access to dj-admin are always allowed
#         if request.user.is_staff:
#             return True
#         if view.action != 'approve':
#             return
