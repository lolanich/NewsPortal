from django.urls import path
from .views import PostList, PostDetail, PostCreate, PostUpdate, PostDelete, search_news

urlpatterns = [
   path('', PostList.as_view()),
   path('<int:pk>', PostDetail.as_view(), name='post_detail'),
   path('create/', PostCreate.as_view(), name='post_edit'),
   path('<int:pk>/update/', PostUpdate.as_view(), name='post_update'),
   path('<int:pk>/delete/', PostDelete.as_view(), name='product_delete'),
   path('search/', search_news, name='news_search'),
]
