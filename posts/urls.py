from django.urls import path
from . import views

urlpatterns = [
    # Post CRUD
    path('', views.PostListView.as_view(), name='post_list'),
    path('post/create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:slug>/update/', views.PostUpdateView.as_view(), name='post_update'),
    path('post/<slug:slug>/delete/', views.PostDeleteView.as_view(), name='post_delete'),

    # Like (AJAX)
    path('post/<slug:slug>/like/', views.like_post, name='like_post'),

    # Comment
    path('post/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    # Kategoriya
    path('category/<slug:slug>/', views.CategoryPostsView.as_view(), name='category_posts'),
]