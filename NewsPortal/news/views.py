from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post
from .filters import NewsFilter
from .forms import PostForm


class PostList(ListView):
    model = Post
    ordering = '-created_at'
    template_name = 'post.html'
    context_object_name = 'post'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = NewsFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'news/post_detail.html'
    context_object_name = 'post'


class PostCreate(CreateView, PermissionRequiredMixin):
    permission_required = '<NewsApp>.<add>_<post>'
    model = Post
    fields = ['author', 'post_type', 'categories', 'title', 'text',]
    template_name = 'news/post_edit.html'
    success_url = reverse_lazy('post_list')


class PostUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = '<NewsApp>.<change>_<post>'
    model = Post
    template_name = 'news/post_edit.html'
    success_url = reverse_lazy('post_list')

    def get_object(self, queryset=None):
        return get_object_or_404(Post, categoryType='news', id=self.kwargs['pk'])


class PostDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'news/post_delete.html'
    success_url = reverse_lazy('post_list')

    def get_object(self, queryset=None):
        return get_object_or_404(Post, categoryType='news', id=self.kwargs['pk'])


def search_news(request):
    query = request.GET.get('query', '')
    author = request.GET.get('author', '')
    date_after = request.GET.get('date_after', '')

    posts_queryset = Post.objects.all()

    if query:
        posts_queryset = posts_queryset.filter(title__icontains=query)

    if author:
        posts_queryset = posts_queryset.filter(
            author__name__icontains=author)

    if date_after:
        posts_queryset = posts_queryset.filter(dateCreations__gte=date_after)

    context = {
        'posts': posts_queryset,
        'query': query,
        'author': author,
        'date_after': date_after,
    }

    return render(request, 'news/post_search.html', context)
