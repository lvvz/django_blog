from django.urls import path, include
from . import views
from .models import ConnectedUser

app_name = 'blog'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('about/', views.about_view, name='about'),

    path('profile/<int:pk>', views.ProfileView.as_view(), name='profile'),
    path('archive', views.PostsView.as_view(), name='archive'),
    path('post/<int:pk>', views.blogpost_view, name='blogpost'),
    path('post/new', views.NewPostView.as_view(), name='new_post'),
    path('comment/<int:pk>/delete', views.delete_comment, name='delete_comment'),
    path('post/<int:pk>/delete', views.delete_post, name='delete_post'),
    path('post/<int:pk>/vote', views.post_vote, name='vote'),

    path('chat', views.chat_view, name='chat'),
    path('chat/connected', views.connected_view, name='connected'),
]

ConnectedUser.objects.all().delete()