"""Utils module. Contains return_user function."""
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
USER = get_user_model()

def return_user(request):
    """Function returns user instance from given request."""
    session_key = request.session.session_key
    session = Session.objects.get(session_key=session_key)
    uid = session.get_decoded().get('_auth_user_id')
    return USER.objects.get(pk=uid)
