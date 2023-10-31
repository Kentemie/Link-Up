from celery import shared_task

from django.core.management import call_command

from .email import send_activate_email_message, send_contact_email_message


@shared_task
def send_activate_email_message_task(user_id):
    """
    1. The task is processed in the view: UserRegisterView
    2. Sending a confirmation letter is carried out through the function: send_activate_email_message
    """

    return send_activate_email_message(user_id)


@shared_task
def send_contact_email_message_task(subject, email, content, ip, user_id):
    """
    1. The task is processed in the view: FeedbackCreateView
    2. Sending a letter from the feedback form is carried out through the function: send_contact_email_message
    """

    return send_contact_email_message(subject, email, content, ip, user_id)


@shared_task
def dbackup_task():
    """
    Performing a database backup
    """

    return call_command('dbackup')