from django.contrib.auth import logout
from django.views.generic import DeleteView
from django.urls import reverse
from django.http import HttpResponseRedirect
from users.tasks import delete_user


class UserDelete(DeleteView):
    '''
    Delete currently connected user
    after backup in a task
    '''
    template_name = 'users/delete.html'

    def get_object(self):
        return self.request.user

    def delete(self, *args, **kwargs):
        user = self.request.user

        # Set user as inactive
        user.is_active = False
        user.save()

        # Backup + Deletion task
        delete_user.delay(user)

        # Disconnect user
        logout(self.request)

        # Redirect to home
        return HttpResponseRedirect(reverse('dashboard'))
