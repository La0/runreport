from rest_framework.permissions import BasePermission

class ClubPremiumPermission(BasePermission):
    message = 'not_premium'

    def has_permission(self, request, view):

        # Check user is connected
        user = request.user
        if not user.is_authenticated():
            return False

        # Check at least a club has full access
        if True not in [c.has_full_access for c in user.club_set.all()]:
            return False

        return True
