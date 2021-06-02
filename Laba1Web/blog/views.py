from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.db.utils import IntegrityError
from django.utils.decorators import method_decorator
from django.views.generic import View, ListView, DetailView, FormView
from django.views.generic.edit import CreateView

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout, get_user_model, views as auth_views, models as auth_models
from django.contrib.auth.forms import AuthenticationForm

from . import models as M
from . import forms as F


def index(request):
    context = dict()
    try:
        context['last_posts'] = M.BlogPost.objects.order_by('-posted')[:5]
    except M.BlogPost.objects.DoesNotExist:
        pass
    return render(request, "blog/index_page.html", context)


class LoginView(auth_views.LoginView):
    template_name = "blog/login_page.html"
    form_class = AuthenticationForm


def logout_view(request):
    logout(request)
    return redirect("blog:index")


class RegisterView(FormView):
    template_name = "blog/register_page.html"
    form_class = F.UserRegisterForm
    success_url = reverse_lazy("blog:index")

    def form_valid(self, form):
        new_user = auth_models.User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'],
                                                        form.cleaned_data['password'])
        new_user.first_name = form.cleaned_data['first_name']
        new_user.last_name = form.cleaned_data['last_name']
        new_user.save()

        blog_user = M.BlogUser()
        blog_user.user = new_user
        blog_user.gender = form.cleaned_data['gender']
        blog_user.birth_date = form.cleaned_data['birth_date']
        try:
            blog_user.save()
        except IntegrityError:
            return super().form_invalid(form)
        login(self.request, user=new_user)
        return super().form_valid(form)


class ProfileView(DetailView):
    model = get_user_model()
    template_name = "blog/profile_page.html"
    context_object_name = 'chosen_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blog_user'] = super().get_object().blog_user
        return context


def blogpost_view(request, pk):
    selected_post = get_object_or_404(M.BlogPost, pk=pk)
    comments = M.Comment.objects.filter(post=selected_post)
    context = {'post': selected_post, 'comments': comments}
    if request.user.is_authenticated:
        comment_form = F.CommentForm()
        if request.method == 'POST':
            comment_form = F.CommentForm(request.POST)
            if comment_form.is_valid():
                saved_comment = comment_form.save(commit=False)
                saved_comment.user = request.user
                saved_comment.post = selected_post
                saved_comment.save()
                return redirect("blog:blogpost", pk)
        context['comment_form'] = comment_form
        try:
            context['vote'] = M.Vote.objects.all().get(user=request.user, post=selected_post)
        except M.Vote.DoesNotExist:
            pass
    return render(request, "blog/blogpost_page.html", context)


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(M.Comment, pk=pk)
    ret_id = comment.post.id
    if request.user == comment.user or request.user.is_staff:
        comment.delete()
        return redirect("blog:blogpost", ret_id)

    return HttpResponseForbidden("GET AWAY")


@login_required
def delete_post(request, pk):
    if request.user.is_staff:
        post = get_object_or_404(M.BlogPost, pk=pk)
        post.delete()
        return redirect("blog:index")
    return HttpResponseForbidden("GET AWAY")


@login_required
def post_vote(request, pk):
    post = get_object_or_404(M.BlogPost, pk=pk)
    up = request.GET.get('up', False)
    if up == "True":
        up = True
    # slow...
    selected_vote, exists = M.Vote.objects.get_or_create(post=post, user=request.user)
    if up:
        if selected_vote.upvote is True:
            return redirect("blog:blogpost", post.id)   # same vote, exit
        elif selected_vote.upvote is False:
            post.downvotes -= 1
        post.upvotes += 1
        selected_vote.upvote = True
    else:
        if selected_vote.upvote is False:
            return redirect("blog:blogpost", post.id)   # same vote, exit
        elif selected_vote.upvote is True:
            post.upvotes -= 1
        post.downvotes += 1
        selected_vote.upvote = False
    selected_vote.save()
    post.save()
    return redirect("blog:blogpost", post.id)


class PostsView(ListView):
    queryset = M.BlogPost.objects.all()
    allow_empty = True
    ordering = '-posted'
    paginate_by = 10
    context_object_name = 'all_posts'
    template_name = "blog/archive_page.html"


class NewPostView(LoginRequiredMixin, CreateView):
    model = M.BlogPost
    template_name = "blog/new_post_page.html"
    form_class = F.PostForm
    success_url = reverse_lazy("blog:index")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        try:
            self.object.author = self.request.user
        except ValueError:
            return HttpResponseForbidden("Get out anon")
        self.object.save()
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_authenticated and request.user.is_staff):  # only staff can post
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


def about_view(request):
    return render(request, "blog/about_page.html")

@login_required
def chat_view(request):
    context = dict()
    context['my_user'] = request.user
    return render(request, 'blog/chat_page.html', context)

@login_required
def connected_view(request):
    if request.user.is_staff:
        connected_users = M.ConnectedUser.objects.all()
        return render(request, 'blog/connected_users_page.html', {'connected_users': connected_users})
    return redirect("blog:index")