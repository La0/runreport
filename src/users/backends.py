from django.contrib.auth.models import check_password
from users.models import Athlete

class EmailAuthBackend(object):
  """
  Email Authentication Backend

  Allows a user to sign in using an email/password pair rather than
  a username/password pair.
  """

  def authenticate(self, username=None, password=None):
    """
    Authenticate a user based on email address as the user name.
    """
    try:
      user = Athlete.objects.get(email=username)
      if user.check_password(password):
        return user
    except Athlete.DoesNotExist:
      return None

  def get_user(self, user_id):
    """
    Get a Athlete object from the user_id.
     """
    try:
      return Athlete.objects.get(pk=user_id)
    except Athlete.DoesNotExist:
      return None
