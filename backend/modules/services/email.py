from django.core.mail import EmailMessage
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse_lazy
from django.conf import settings


User = get_user_model()


def send_contact_email_message(subject, email, content, ip, user_id):
    """
    Function of sending a letter from the feedback form
    """

    user = User.objects.get(id=user_id) if user_id else None
    message = render_to_string('system/email/feedback_email_send.html', {
        'email': email,
        'content': content,
        'ip': ip,
        'user': user,
    })
    email = EmailMessage(subject, message, settings.SERVER_EMAIL, [settings.EMAIL_ADMIN])
    email.send(fail_silently=False)


def send_activate_email_message(user_id):
    """
    Function of sending an account confirmation email
    """

    user = get_object_or_404(User, id=user_id)
    current_site = Site.objects.get_current().domain
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    activation_url = reverse_lazy('system:confirm_email', kwargs={'uidb64': uid, 'token': token})
    subject = f'Activate your account, {user.username}!'
    message = render_to_string('system/email/activate_email_send.html', {
        'user': user,
        'activation_url': f'http://{current_site}{activation_url}',
    })

    return user.email_user(subject, message)