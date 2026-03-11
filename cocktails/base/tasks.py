import logging
from os import environ
from smtplib import SMTPRecipientsRefused
from typing import Union, List

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.translation import activate

from main_core.celery import celery_app

logger = logging.getLogger(__name__)


__all__ = [
    'except_shell',
    'smtp_shell',
    'send_mail',
    'consume_send_mail',
]


def except_shell(errors=(Exception,), default_value=None):
    def decorator(func):
        def new_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except errors as e:
                logging.error(e)
                return default_value
        return new_func
    return decorator


smtp_shell = except_shell((SMTPRecipientsRefused,), default_value=False)


@celery_app.task(name='email.send_mail')
def send_mail(
    subject: str,
    template_name: str,
    context: dict,
    to_email: Union[List[str], str],
    letter_language: str = 'en',
    **kwargs,
):
    """
    :param subject: email subject
    :param template_name: template path to email template
    :param context: data what will be passed into email
    :param to_email: receiver email(s)
    :param letter_language: translate letter to selected lang
    :param kwargs: from_email, bcc, cc, reply_to and file_path params
    """
    if to_email in ('testuser', 'testuser2', 'testuser_reg_jj'):
        return
    activate(letter_language)
    to_email: list = [to_email] if isinstance(to_email, str) else to_email
    email_message = EmailMultiAlternatives(
        subject=subject,
        from_email=kwargs.get('from_email') or settings.EMAIL_HOST_USER,
        to=to_email,
        bcc=kwargs.get('bcc'),
        cc=kwargs.get('cc'),
        reply_to=kwargs.get('reply_to'),
    )
    context['settings'] = settings
    html_email: str = loader.render_to_string(template_name, context)
    #if settings.DEBUG:
    #    logger.warning(html_email)
    #    return
    email_message.attach_alternative(html_email, 'text/html')
    if file_path := kwargs.get('file_path'):
        file_path = environ.get('APP_HOME', environ.get('HOME')) + file_path
        email_message.attach_file(file_path, kwargs.get('mimetype'))
    return consume_send_mail(email_message)


@smtp_shell
def consume_send_mail(email_message: EmailMultiAlternatives):
    email_message.send()
    return True
