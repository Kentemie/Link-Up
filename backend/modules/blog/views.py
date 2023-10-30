from random import shuffle

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.query import QuerySet
from django.shortcuts import redirect
from django.urls import reverse_lazy

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

from typing import Any

from .models import Article, Category, Comment, Rating
from .forms import ArticleCreateForm, ArticleUpdateForm, CommentCreateForm

from ..services.mixins import AuthorRequiredMixin
from ..services.utils  import get_client_ip

from taggit.models import Tag



class ArticleListView(ListView):

    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'
    paginate_by = 5

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home page'
        return context
    


class ArticleDetailView(DetailView):

    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'
    queryset = model.objects.detail()

    def get_similar_articles(self, obj):
        article_tags_ids = obj.tags.values_list('id', flat=True)
        similar_articles = Article.objects\
            .filter(tags__in=article_tags_ids)\
            .exclude(id=obj.id)\
            .annotate(related_tags=Count('tags'))\
            .order_by('-related_tags')
        similar_articles_list = list(similar_articles.all())
        shuffle(similar_articles_list)
        return similar_articles_list[:6]


    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        context['form'] = CommentCreateForm
        context['similar_articles'] = self.get_similar_articles(self.object)
        return context
    


class ArticleByCategoryListView(ListView):

    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10
    category = None
    
    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs['slug'])
        queryset = Article.objects.filter(category__slug=self.category.slug)
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = f'Articles from the category: {self.category.title}' 
        return context



class ArticleByTagListView(ListView):

    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10
    tag = None

    def get_queryset(self):
        self.tag = Tag.objects.get(slug=self.kwargs['tag'])
        queryset = Article.objects.all().filter(tags__slug=self.tag.slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Articles by tag: {self.tag.name}'
        return context
    


class ArticleBySignedUser(LoginRequiredMixin, ListView):
    """
    A view that displays a list of articles by authors that the current user is subscribed to
    """

    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'
    login_url = 'login'
    paginate_by = 10

    def get_queryset(self):
        authors = self.request.user.profile.following.values_list('id', flat=True)
        queryset = self.model.objects.all().filter(author_id__in=authors)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Articles by authors' 
        return context
    


class ArticleCreateView(LoginRequiredMixin, CreateView):

    model = Article
    template_name = 'blog/article_create.html'
    form_class = ArticleCreateForm
    login_url = 'blog:home'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Adding an article to the site'
        return context
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)



class ArticleUpdateView(AuthorRequiredMixin, SuccessMessageMixin, UpdateView):

    model = Article
    template_name = 'blog/article_update.html'
    context_object_name = 'article'
    form_class = ArticleUpdateForm
    login_url = 'blog:home'
    success_message = 'The article has been successfully updated'

    def get_context_data(self, *, object_list=None, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = f'Article update: {self.object.title}'
        return context
    
    def form_valid(self, form):
        # form.instance.the_one_who_updated = self.request.user
        form.save()
        return super().form_valid(form)
    


class ArticleDeleteView(AuthorRequiredMixin, DeleteView):

    model = Article
    success_url = reverse_lazy('blog:home')
    context_object_name = 'article'
    template_name = 'blog/article_delete.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Deleting an article: {self.object.title}'
        return context
    


class CommentCreateView(LoginRequiredMixin, CreateView):

    model = Comment
    form_class = CommentCreateForm

    def is_ajax(self):
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    def form_invalid(self, form):
        if self.is_ajax():
            return JsonResponse({'error': form.errors}, status=400)
        return super().form_invalid(form)
    
    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.article_id = self.kwargs.get('pk')
        comment.author = self.request.user
        comment.parent_id = form.cleaned_data.get('parent')
        comment.save()

        if self.is_ajax():
            return JsonResponse({
                'is_child': comment.is_child_node(),
                'id': comment.id,
                'author': comment.author.username,
                'parent_id': comment.parent_id,
                'created_at': comment.created_at.strftime('%Y-%b-%d %H:%M:%S'),
                'avatar': comment.author.profile.avatar.url,
                'content': comment.content,
                'get_absolute_url': comment.author.profile.get_absolute_url()
            }, status=200)
        
        return redirect(comment.article.get_absolute_url())
    
    def handle_no_permission(self):
        return JsonResponse({'error': 'You must be logged in to add comments'}, status=400)
    


class ArticleSearchResultView(ListView):
    """
    Implementation of search for articles on the site
    """

    model = Article
    context_object_name = 'articles'
    paginate_by = 10
    allow_empty = True
    template_name = 'blog/article_list.html'

    def get_queryset(self) -> QuerySet[Any]:
        query = self.request.GET.get('do')
        search_vector = SearchVector('full_description', weight='B') + SearchVector('title', weight='A')
        search_query = SearchQuery(query)
        return (self.model.objects.annotate(rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank'))
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = f'Searching results: {self.request.GET.get("do")}'
        return context
    
    """
    The get_queryset() method searches for articles using the full-text search engine from the django.contrib.postgres.search module 
    in PostgreSQL. To do this, a search vector (search_vector) is formed containing the fields that will be searched, and the weights
    of each field are set. Then a search query (search_query) is generated based on the user request (query), which was passed 
    through the GET parameter do. The search is performed using the SearchRank and filter methods of the Article model. The 
    results are sorted by relevance in reverse order.

    The get_context_data() method generates a context for displaying found articles in the template.
    """



class RatingCreateView(View):

    model = Rating

    def post(self, request, *args, **kwargs):
        article_id = request.POST.get('article_id')
        value = int(request.POST.get('value'))
        ip_address = get_client_ip(request)
        user = request.user if request.user.is_authenticated else None
        
        rating, created = self.model.objects.get_or_create(
            article_id=article_id,
            ip_address=ip_address,
            defaults={'value': value, 'user': user},
        )
        
        if not created:
            if rating.value == value:
                rating.delete()
                return JsonResponse({'status': 'deleted', 'rating_sum': rating.article.get_sum_rating()})
            else:
                rating.value = value
                rating.user = user
                rating.save()
                return JsonResponse({'status': 'updated', 'rating_sum': rating.article.get_sum_rating()})
            
        return JsonResponse({'status': 'created', 'rating_sum': rating.article.get_sum_rating()})