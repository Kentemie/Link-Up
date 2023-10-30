from django.urls import path

from .views import (
    ArticleListView, ArticleDetailView,
    ArticleByCategoryListView, ArticleByTagListView,
    ArticleCreateView, ArticleUpdateView,
    ArticleDeleteView, CommentCreateView,
    ArticleSearchResultView, RatingCreateView,
    ArticleBySignedUser,
)


app_name = 'blog'

urlpatterns = [
    path('articles/', ArticleListView.as_view(), name='home'),
    path('articles/create/', ArticleCreateView.as_view(), name='article_create'),
    path('articles/signed/', ArticleBySignedUser.as_view(), name='articles_by_signed_user'),
    path('articles/<slug:slug>/update/', ArticleUpdateView.as_view(), name='article_update'),
    path('articles/<slug:slug>/delete/', ArticleDeleteView.as_view(), name='article_delete'),
    path('articles/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),
    path('articles/<int:pk>/comments/create/', CommentCreateView.as_view(), name='comment_create_view'),
    path('articles/tags/<str:tag>/', ArticleByTagListView.as_view(), name='articles_by_tags'),
    path('category/<slug:slug>/', ArticleByCategoryListView.as_view(), name="articles_by_category"),
    path('search/', ArticleSearchResultView.as_view(), name='search'),
    path('rating/', RatingCreateView.as_view(), name='rating'),

]