from django.urls import path
from .views import PostList, PostDetail, PostCreate, PostUpdate, PostDelete, search_news, CategoryList, subscribe

urlpatterns = [
   path('', PostList.as_view(),  name='post_list'),
   path('<int:pk>/', PostDetail.as_view(), name='post_detail'),
   path('create/', PostCreate.as_view(), name='post_edit'),
   path('<int:pk>/update/', PostUpdate.as_view(), name='post_update'),
   path('<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
   path('search/', search_news, name='news_search'),
   path('categories/<int:pk>/', CategoryList.as_view(), name='category_list'),
   path('categories/<int:pk>/subscribe/', subscribe, name='subscribe'),
]
