from django.views.generic import (
    View, 
    DetailView, 
    UpdateView, 
    CreateView, 
    TemplateView
)
from django.contrib.auth.views import (
    LoginView, 
    LogoutView,
    PasswordChangeView, 
    PasswordResetView, 
    PasswordResetConfirmView
)
from django.db import transaction
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse_lazy

from .models import Profile, Feedback
from .forms import (
    UserUpdateForm, 
    ProfileUpdateForm, 
    UserRegisterForm, 
    UserLoginForm, 
    UserPasswordChangeForm,
    UserForgotPasswordForm,
    UserSetNewPasswordForm,
    FeedbackCreateForm,
)

from ..services.mixins import UserIsNotAuthenticated
from ..services.utils import get_client_ip
from ..services.tasks import send_activate_email_message_task, send_contact_email_message_task



User = get_user_model()



class ProfileDetailView(DetailView):

    model = Profile
    context_object_name = 'profile'
    template_name = 'system/profile_detail.html'
    queryset = model.objects.all().select_related('user').prefetch_related('followers', 'followers__user', 'following', 'following__user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'User page: {self.object.user.username}'
        return context



class ProfileUpdateView(UpdateView):

    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'system/profile_edit.html'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Editing a User Profile: {self.request.user.username}'
        if self.request.POST:
            context['user_form'] = UserUpdateForm(self.request.POST, instance=self.request.user)
        else:
            context['user_form'] = UserUpdateForm(instance=self.request.user)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        with transaction.atomic():
            if all([form.is_valid(), user_form.is_valid()]):
                user_form.save()
                form.save()
            else:
                context.update({'user_form': user_form})
                return self.render_to_response(context)
        return super(ProfileUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('system:profile_detail', kwargs={'slug': self.object.slug})
    


class UserLoginView(SuccessMessageMixin, LoginView):

    form_class = UserLoginForm
    template_name = 'system/registration/user_login.html'
    next_page = 'blog:home'
    success_message = 'Welcome to the site!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Authorization on the site'
        return context
    


class UserLogoutView(LogoutView):

    next_page = 'blog:home'



class UserPasswordChangeView(SuccessMessageMixin, PasswordChangeView):

    form_class = UserPasswordChangeForm
    template_name = 'system/registration/user_password_change.html'
    success_message = 'Your password has been successfully changed!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Changing your password on the site'
        return context

    def get_success_url(self):
        return reverse_lazy('system:profile_detail', kwargs={'slug': self.request.user.profile.slug})
    


class UserForgotPasswordView(SuccessMessageMixin, PasswordResetView):

    form_class = UserForgotPasswordForm
    template_name = 'system/registration/user_password_reset.html'
    success_url = reverse_lazy('blog:home')
    success_message = 'A letter with password recovery instructions has been sent to your email'
    subject_template_name = 'system/email/password_subject_reset_mail.txt'
    email_template_name = 'system/email/password_reset_mail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Password recovery request'
        return context



class UserPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):

    form_class = UserSetNewPasswordForm
    template_name = 'system/registration/user_password_set_new.html'
    success_url = reverse_lazy('blog:home')
    success_message = 'The password has been successfully changed. You can log in to the site'
               
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Set a new password'
        return context



# <-- Views for user registration -->



class UserRegisterView(UserIsNotAuthenticated, CreateView):

    form_class = UserRegisterForm
    success_url = reverse_lazy('blog:home')
    template_name = 'system/registration/user_register.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registration on the site'
        return context
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # Asynchronously, using celery, an activation letter is sent to the new user's email.
        send_activate_email_message_task.delay(user.id)
        return redirect('system:email_confirmation_sent')



class UserConfirmEmailView(View):

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        
        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return redirect('system:email_confirmed')
        else:
            return redirect('system:email_confirmation_failed')
        

    
class EmailConfirmationSentView(TemplateView):

    template_name = 'system/registration/email_confirmation_sent.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Activation email sent'
        return context



class EmailConfirmedView(TemplateView):

    template_name = 'system/registration/email_confirmed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Your account has been activated'
        return context



class EmailConfirmationFailedView(TemplateView):

    template_name = 'system/registration/email_confirmation_failed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Your account is not activated'
        return context
    


# <-- Feedback -->



class FeedbackCreateView(SuccessMessageMixin, CreateView):

    model = Feedback
    form_class = FeedbackCreateForm
    success_message = 'Your letter has been successfully sent to the site administration'
    template_name = 'system/feedback.html'
    extra_context = {'title': 'Contact form'}
    success_url = reverse_lazy('blog:home')

    def form_valid(self, form):
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.ip_address = get_client_ip(self.request)
            if self.request.user.is_authenticated:
                feedback.user = self.request.user
            send_contact_email_message_task.delay(feedback.subject, feedback.email, feedback.content, feedback.ip_address, feedback.user_id)
        return super().form_valid(form)
    


@method_decorator(login_required, name='dispatch')
class ProfileFollowingCreateView(View):
    """
    Create a subscription for users
    """

    model = Profile

    def is_ajax(self):
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def post(self, request, slug):
        user = self.model.objects.get(slug=slug)
        profile = request.user.profile
        if profile in user.followers.all():
            user.followers.remove(profile)
            message = f'Subscribe to {user}'
            status = False
        else:
            user.followers.add(profile)
            message = f'Unsubscribe from {user}'
            status = True
        data = {
            'username': profile.user.username,
            'get_absolute_url': profile.get_absolute_url(),
            'slug': profile.slug,
            'avatar': profile.get_avatar,
            'message': message,
            'status': status,
        }
        return JsonResponse(data, status=200)



# <-- Custom templates for error pages 403, 404, 500 -->


def tr_handler404(request, exception):
    """
    Handling error 404
    """
    return render(request=request, template_name='system/errors/error_page.html', status=404, context={
        'title': 'Page not found: 404',
        'error_message': 'Sorry, this page was not found or has been moved', 
    })


def tr_handler500(request):
    """
    Handling error 500
    """
    return render(request=request, template_name='system/errors/error_page.html', status=500, context={
        'title': 'Server error: 500',
        'error_message': 'Internal site error, return to the main page, we will send an error report to the site administration',
    })


def tr_handler403(request, exception):
    """
    Handling error 403
    """
    return render(request=request, template_name='system/errors/error_page.html', status=403, context={
        'title': 'Access error: 403',
        'error_message': 'Access to this page is restricted',
    })