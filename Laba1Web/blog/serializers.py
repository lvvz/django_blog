from rest_framework import serializers,  permissions, validators
from rest_framework import routers, viewsets, permissions, response, status
from rest_framework.exceptions import ParseError

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from . import models as M


class UserSerializer(serializers.ModelSerializer):
    comments = serializers.HyperlinkedRelatedField(view_name='comment-detail', queryset=M.Comment.objects.all(), many=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'blog_user', 'first_name', 'last_name', 'is_staff', 'comments']  #
        depth = 1


class PostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = M.BlogPost
        fields = ['url', 'id', 'title', 'content', 'author', 'posted', 'upvotes', 'downvotes', 'comments']


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = M.Comment
        fields = ['id', 'user', 'post', 'text', 'posted']  #


class VoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = M.Vote
        fields = ['id', 'user', 'post', 'upvote']


class PostViewSet(viewsets.ModelViewSet):
    queryset = M.BlogPost.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get', 'post', 'patch', 'delete']


class CommentViewSet(viewsets.ModelViewSet):
    queryset = M.Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class VoteViewSet(viewsets.ModelViewSet):
    queryset = M.Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get', 'post', 'delete']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get']


MyApiRouter = routers.DefaultRouter()

MyApiRouter.register(r'blogposts', PostViewSet)
MyApiRouter.register(r'users', UserViewSet)
MyApiRouter.register(r'comments', CommentViewSet)
MyApiRouter.register(r'votes', VoteViewSet)
