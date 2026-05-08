from .models import Profile


def user_role(request):
    if not request.user.is_authenticated:
        return {'user_role': 'guest'}
    try:
        return {'user_role': request.user.profile.role}
    except Profile.DoesNotExist:
        return {'user_role': 'patient'}
