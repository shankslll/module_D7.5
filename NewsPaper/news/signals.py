from django.shortcuts import render, redirect
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Post
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import mail_admins
from django.contrib.sites.shortcuts import get_current_site


@receiver(post_save, sender=User)
def user_greeting(sender, instance, created, **kwargs):
    if created:
        usr = instance.username
        html_content = render_to_string(
            'simpleapp/greeting_email.html',
                {
                'usr': usr,
                }
        )
        msg = EmailMultiAlternatives(
            subject='Регистрация на портале',
            body=f'Здравствуйте, {usr}. Спасибо за регистрацию на нашем портале!',
            from_email='vymorkoff2016@yandex.ru',
            to=[f'{instance.email}'],  # это то же, что и recipients_list
        )
        msg.attach_alternative(html_content, "text/html")  # добавляем html

        msg.send()  # отсылаем


@receiver(m2m_changed, sender=Post.postCategory.through)
def notify_users_news(sender, instance, action, **kwargs):
    full_url = ''.join(['http://', get_current_site(None).domain, ':8000'])
    if action == "post_add":
        list_of_subscribers = []
        for c in instance.postCategory.all():
            for usr in c.subscribers.all():
                list_of_subscribers.append(usr)
        for usr in list_of_subscribers:

            html_content = render_to_string(
                'simpleapp/subs_email.html',
                {
                    'post': instance,
                    'usr': usr,
                    'full_url': full_url,
                }
            )
            msg = EmailMultiAlternatives(
                subject=instance.name,
                body=f'Здравствуйте, {usr.username}. Новая статья в твоём любимом разделе!',
                # это то же, что и message
                from_email='vymorkoff2016@yandex.ru',
                to=[f'{usr.email}'],  # это то же, что и recipients_list
            )
            msg.attach_alternative(html_content, "text/html")  # добавляем html

            msg.send()