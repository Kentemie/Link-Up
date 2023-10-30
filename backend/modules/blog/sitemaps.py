from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Article



class ArticleSitemap(Sitemap):

    changefreq = 'monthly'
    priority = 0.9
    protocol = 'https'

    def items(self):
        return Article.objects.all()

    def lastmod(self, obj):
        return obj.updated_at
    


class StaticSitemap(Sitemap):

    def items(self):
        return ['system:feedback', 'blog:home']
    
    def location(self, item):
        return reverse(item)