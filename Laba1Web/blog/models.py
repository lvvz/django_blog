from django.db import models
from django.conf import settings


class BlogUser(models.Model):
    gender_choices = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('None', 'Unspecified')
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_user')
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=gender_choices, default='None')

    def __str__(self):
        return self.user.username


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.CharField(max_length=1000)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    posted = models.DateTimeField(auto_now_add=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)

    def __str__(self):
        return self.title + ' ' + self.author.username


class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='comments')
    text = models.CharField(max_length=500, blank=False)
    posted = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.pk) + ' ' + self.post.title + ' ' + self.user.username


class Vote(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    upvote = models.BooleanField(null=True)

    def __str__(self):
        return self.post.title + ' ' + self.user.username + ' ' + str(self.upvote)


class ConnectedUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='connected_user', default=0, editable=False, unique=True)
    connected = models.TimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
