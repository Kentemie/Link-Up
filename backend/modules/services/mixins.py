from django.contrib.auth.mixins import AccessMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import redirect

from ..blog.models import Viewer

from .utils import get_client_ip



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
    


class CountViewerMixin:
    """
    Mixin to increase article view count
    """

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if hasattr(self.object, 'viewers'):
            viewer, _ = Viewer.objects.get_or_create(
                user=request.user if request.user.is_authenticated else None,
                ip_address=get_client_ip(request)
            )
            print(self.object.viewers.all())

            if self.object.viewers.filter(id=viewer.id).count() == 0:
                self.object.viewers.add(viewer)
 
        return response