from allauth.account.signals import email_confirmed
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed, pre_save
from django.dispatch import receiver
from django.core.mail import mail_managers, send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from .models import PostCategory, Post


@receiver(m2m_changed, sender=PostCategory)
def notify_managers_appointment(sender, instance, action, **kwargs):
    if action == 'post_add':
        emails = set(
            User.objects.filter(subscribed_categories__in=instance.categories.all()).distinct().values_list('email', flat=True))

        html_title = render_to_string('news/title.html', {'title': instance.title})
        from django.utils.html import strip_tags
        plain_text_preview = strip_tags(instance.text)[:50]

        for email in emails:
            try:
                user = User.objects.get(email=email)
                username = user.username
            except User.DoesNotExist:
                username = 'Пользователь'

            try:
                send_mail(
                    subject=instance.title,
                    message='',
                    from_email='t.maill@yandex.ru',
                    recipient_list=[user.email],
                    html_message=render_to_string('news/email_template.html', {
                        'title': instance.title,
                        'html_title': html_title,
                        'username': username,
                        'preview_text': plain_text_preview,
                    }),
                )
            except Exception as e:
                print(f"Ошибка при отправке письма {email}: {e}")


@receiver(pre_save, sender=Post)
def stop_post(sender, instance, **kwargs):
    if not instance.pk:
        now = timezone.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        count = Post.objects.filter(
            author=instance.author,
            post_type=instance.post_type,
            created_at__gte=start_of_day,
            created_at__lte=now
        ).count()
        if count >= 3:
            raise ValidationError("Вы не можете публиковать более 3 новостей в сутки.")


@receiver(email_confirmed)
def send_welcome_email(request, email_address, **kwargs):
    user = email_address.user
    subject = 'Добро пожаловать!'
    from_email = 't.maill@yandex.ru'
    recipient_list = [user.email]
    html_content = render_to_string('account/email_confirmation_signup_message.html', {'user': user})
    msg = EmailMultiAlternatives(subject, '', from_email, recipient_list)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


