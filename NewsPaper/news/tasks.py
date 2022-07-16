from celery import shared_task
import time
import datetime
from django.shortcuts import render, redirect
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import mail_admins
from django.contrib.sites.shortcuts import get_current_site
from .models import Post


@shared_task
def notify_users_news(pk):
    full_url = ''.join(['http://', get_current_site(None).domain, ':8000'])
    instance = Post.objects.get(pk=pk)
    list_of_subscribers = []
    for c in instance.postCategory.all():
        for usr in c.subscribers.all():
            list_of_subscribers.append(usr)
    for usr in list_of_subscribers:

        html_content = render_to_string(
            'subs_email.html',
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


@shared_task
def news_every_week():
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=7)
    full_url = ''.join(['http://', get_current_site(None).domain, ':8000'])

    for u in User.objects.all():
        if len(u.category_set.all()) > 0:
            list_of_posts = Post.objects.filter(news_data__range=(start_date, end_date), postCategory__in=u.category_set.all())
            html_content = render_to_string(
                'subs_email_each_week.html',
                {
                    'news': list_of_posts,
                    'usr': u,
                    'full_url': full_url,
                }
            )
            msg = EmailMultiAlternatives(
                subject=f'Здравствуй, {u.username}. Список статей за неделю с нашего портала!',
                body='',
                # это то же, что и message
                from_email='vymorkoff2016@yandex.ru',
                to=[f'{u.email}'],  # это то же, что и recipients_list
            )
            msg.attach_alternative(html_content, "text/html")  # добавляем html

            msg.send()