from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from .forms import PostForm
from .models import Post, Category
from .filters import PostFilter
from django.urls import reverse_lazy, path
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models.signals import post_save, m2m_changed
from django.contrib.sites.shortcuts import get_current_site
from django.dispatch import receiver
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.views import View
from .tasks import notify_users_news


# Я так и не понял как сделать отдельно создание новостей и статей(((((((
@receiver(post_save, sender=User)
def user_greeting(sender, instance, created, **kwargs):
    if created:
        usr = instance.username
        html_content = render_to_string(
            'greeting_email.html',
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


class PostList(ListView):
    model = Post
    ordering = '-dateCreation'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'message.html'
    context_object_name = 'new'


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'

    def form_valid(self, form):
        news = form.save(commit=False)
        news.categoryType = "NEWS"
        return super().form_valid(form)


class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'


class PostDelete(DeleteView):
    model = Post
    template_name = 'news_delete.html'
    success_url = reverse_lazy('news_list')


class PostSearch(ListView):
    model = Post
    ordering = '-dateCreation'
    template_name = 'search.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class CategoryList(ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'
    paginate_by = 3


@login_required
def subscribe_me(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    if category not in user.category_set.all():
        category.subscribers.add(user)
        return redirect('/news/category/')


@login_required
def unsubscribe_me(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    if category in user.category_set.all():
        category.subscribers.remove(user)
        return redirect('/news/category/')


class IndexView(View):
    def get(self, request):
        hello.delay()
        return HttpResponse('Hello!')