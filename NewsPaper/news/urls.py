from django.urls import path
from .views import (
    PostList, PostDetail, PostCreate, PostUpdate, PostDelete, PostSearch,CategoryList, subscribe_me, unsubscribe_me, IndexView
)

urlpatterns = [
    path('', PostList.as_view(), name='post_list'),
    path('<int:pk>', PostDetail.as_view(), name='post_detail'),
    path('search/', PostSearch.as_view(), name='post_search'),
    path('create/', PostCreate.as_view(), name='product_create'),
    path('<int:pk>/update/', PostUpdate.as_view(), name='post_update'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('category/', CategoryList.as_view(), name='category_list'),
    path('category/subscribe/<int:pk>', subscribe_me),
    path('category/unsubscribe/<int:pk>', unsubscribe_me),
    path('', IndexView.as_view()),
    #path('', AppointmentView.as_view()),
]
