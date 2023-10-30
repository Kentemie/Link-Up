from django.contrib.auth.mixins import AccessMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import redirect



class AuthorRequiredMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user != self.get_object().author or not request.user.is_superuser:
            messages.info(request, 'Changing and deleting an article is available only to the author or to the admin')
            return redirect('blog:home')

        return super().dispatch(request, *args, **kwargs)
    


class UserIsNotAuthenticated(UserPassesTestMixin):

    def test_func(self) -> bool | None:
        if self.request.user.is_authenticated:
            messages.info(self.request, 'You are already logged in. You cannot visit this page')
            raise PermissionDenied
        return True
    
    def handle_no_permission(self):
        return redirect('blog:home')