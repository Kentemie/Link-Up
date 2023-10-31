from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
from django.urls import reverse

from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field

from ..services.utils import unique_slugify, image_compress



User = get_user_model()
    


class ArticleManager(models.Manager):

    def all(self):
        return self.get_queryset()\
                .select_related('author', 'category')\
                .prefetch_related('ratings', 'viewers')\
                .filter(status='P')
    
    def detail(self):
        return self.get_queryset()\
                .select_related('author', 'category')\
                .prefetch_related('comments', 'comments__author', 'comments__author__profile', 'tags', 'ratings')\
                .filter(status='P')



class Category(MPTTModel):

    class MPTTMeta:
        order_insertion_by = ('title',)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        db_table = 'app_categories'

    
    title = models.CharField(
        max_length=255, 
        verbose_name='Category name'
    )
    slug = models.SlugField(
        max_length=255, 
        verbose_name='Category URL', 
        blank=True
    )
    description = models.TextField(
        verbose_name='Category description', 
        max_length=300
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True,
        related_name='children',
        verbose_name='Parent category'
    )


    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:articles_by_category', kwargs={'slug': self.slug})
    


class Viewer(models.Model):
    """
    Article views model
    """

    class Meta:
        ordering = ('-viewed_on',)
        indexes = [models.Index(fields=['-viewed_on'])]
        verbose_name = 'Viewer'
        verbose_name_plural = 'Viewers'


    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        related_name='user_viewer',
        blank=True,
        null=True
    )
    ip_address = models.GenericIPAddressField(
        verbose_name='IP address',
    )
    viewed_on = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Date viewed'
    )


    def __str__(self):
        return f'{self.user}-{self.ip_address}'



class Article(models.Model):

    class Meta:
        db_table = 'app_articles'
        ordering = ['-fixed', '-created_at']
        indexes = [models.Index(fields=['-fixed', '-created_at', 'status'])]
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    
    STATUS_OPTIONS = (
        ('P', 'Published'),
        ('D', 'Draft'),
    )

    title = models.CharField(
        verbose_name='Title', 
        max_length=255
    )
    slug = models.SlugField(
        verbose_name='URL', 
        max_length=255, 
        blank=True, 
        unique=True
    )
    author = models.ForeignKey(
        to=User, 
        verbose_name='Author', 
        on_delete=models.SET_DEFAULT, 
        related_name='posts_author', 
        default=1
    )
    the_one_who_updated = models.ForeignKey(
        to=User, 
        verbose_name='The one who updated', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='posts_updater', 
        blank=True
    )
    category = TreeForeignKey(
        'Category', 
        on_delete=models.PROTECT, 
        related_name='articles', 
        verbose_name='Category'
    )
    viewers = models.ManyToManyField(
        Viewer,
        verbose_name='Views',
        related_name='article_viewers',
        blank=True
    )
    short_description = CKEditor5Field(
        verbose_name='Short description', 
        max_length=500,
        config_name='extends'
    )
    full_description = CKEditor5Field(
        verbose_name='Full description',
        config_name='extends'
    )
    thumbnail = models.ImageField(
        verbose_name='Post preview', 
        blank=True, 
        upload_to='images/thumbnails/%Y/%m/%d/', 
        validators=[
            FileExtensionValidator(allowed_extensions=('png', 'jpg', 'webp', 'jpeg', 'gif'))
        ]
    )
    status = models.CharField(
        choices=STATUS_OPTIONS, 
        default='Published', 
        verbose_name='Post status', 
        max_length=10
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Add time'
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name='Update time'
    )
    fixed = models.BooleanField(
        verbose_name='Recorded', 
        default=False
    )


    tags = TaggableManager()
    objects = ArticleManager()

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__thumbnail = self.thumbnail if self.pk else None

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:article_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)

        if self.__thumbnail != self.thumbnail and self.thumbnail:
            image_compress(self.thumbnail.path, width=500, height=500)

    def get_sum_rating(self):
        return sum([rating.value for rating in self.ratings.all()])
    


class Comment(MPTTModel):

    class MTTMeta:
        order_insertion_by = ('-created_at',)

    class Meta:
        db_table = 'app_comments'
        indexes = [models.Index(fields=['-created_at', 'updated_at', 'status', 'parent'])]
        ordering = ['-created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'


    STATUS_OPTIONS = (
        ('P', 'Published'),
        ('D', 'Draft'),
    )

    article = models.ForeignKey(
        Article, 
        on_delete=models.CASCADE, 
        verbose_name='Comment', 
        related_name='comments'
    )
    author = models.ForeignKey(
        User, 
        verbose_name='Author of the comment', 
        on_delete=models.CASCADE, 
        related_name='comments_author'
    )
    content = models.TextField(
        verbose_name='Comment text', 
        max_length=3000
    )
    created_at = models.DateTimeField(
        verbose_name='Add time', 
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name='Update time',
        auto_now=True
    )
    status = models.CharField(
        choices=STATUS_OPTIONS, 
        default='Published',
        verbose_name='Comment status',
        max_length=10
    )
    parent = TreeForeignKey(
        'self', 
        verbose_name='Parental comment', 
        null=True, 
        blank=True, 
        related_name='children', 
        on_delete=models.CASCADE
    )


    def __str__(self):
        return f'{self.author}:{self.content}'
    


class Rating(models.Model):

    class Meta:
        unique_together = ('article', 'ip_address')
        ordering = ('-created_at',)
        indexes = [models.Index(fields=['-created_at', 'value'])]
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'

    
    article = models.ForeignKey(
        to=Article, 
        verbose_name='Article', 
        on_delete=models.CASCADE, 
        related_name='ratings'
    )
    user = models.ForeignKey(
        to=User, 
        verbose_name='User', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True
    )
    value = models.IntegerField(
        verbose_name='Value', 
        choices=[
            (1, 'Like'), 
            (-1, 'Dislike')
        ]
    )
    created_at = models.DateTimeField(
        verbose_name='Add time', 
        auto_now_add=True
    )
    ip_address = models.GenericIPAddressField(
        verbose_name='IP address'
    )


    def __str__(self):
        return self.article