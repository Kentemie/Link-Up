# Generated by Django 4.2.6 on 2023-10-30 19:57

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_ckeditor_5.fields
import mptt.fields
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Category name')),
                ('slug', models.SlugField(blank=True, max_length=255, verbose_name='Category URL')),
                ('description', models.TextField(max_length=300, verbose_name='Category description')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='blog.category', verbose_name='Parent category')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'db_table': 'app_categories',
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('slug', models.SlugField(blank=True, max_length=255, unique=True, verbose_name='URL')),
                ('short_description', django_ckeditor_5.fields.CKEditor5Field(max_length=500, verbose_name='Short description')),
                ('full_description', django_ckeditor_5.fields.CKEditor5Field(verbose_name='Full description')),
                ('thumbnail', models.ImageField(blank=True, upload_to='images/thumbnails/%Y/%m/%d/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=('png', 'jpg', 'webp', 'jpeg', 'gif'))], verbose_name='Post preview')),
                ('status', models.CharField(choices=[('P', 'Published'), ('D', 'Draft')], default='Published', max_length=10, verbose_name='Post status')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Add time')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Update time')),
                ('fixed', models.BooleanField(default=False, verbose_name='Recorded')),
                ('author', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='posts_author', to=settings.AUTH_USER_MODEL, verbose_name='Author')),
                ('category', mptt.fields.TreeForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='articles', to='blog.category', verbose_name='Category')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
                ('the_one_who_updated', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts_updater', to=settings.AUTH_USER_MODEL, verbose_name='The one who updated')),
            ],
            options={
                'verbose_name': 'Post',
                'verbose_name_plural': 'Posts',
                'db_table': 'app_articles',
                'ordering': ['-fixed', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(choices=[(1, 'Like'), (-1, 'Dislike')], verbose_name='Value')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Add time')),
                ('ip_address', models.GenericIPAddressField(verbose_name='IP address')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='blog.article', verbose_name='Article')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Rating',
                'verbose_name_plural': 'Ratings',
                'ordering': ('-created_at',),
                'indexes': [models.Index(fields=['-created_at', 'value'], name='blog_rating_created_7cb6e7_idx')],
                'unique_together': {('article', 'ip_address')},
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=3000, verbose_name='Comment text')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Add time')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Update time')),
                ('status', models.CharField(choices=[('P', 'Published'), ('D', 'Draft')], default='Published', max_length=10, verbose_name='Comment status')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='blog.article', verbose_name='Comment')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments_author', to=settings.AUTH_USER_MODEL, verbose_name='Author of the comment')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='blog.comment', verbose_name='Parental comment')),
            ],
            options={
                'verbose_name': 'Comment',
                'verbose_name_plural': 'Comments',
                'db_table': 'app_comments',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['-created_at', 'updated_at', 'status', 'parent'], name='app_comment_created_4bf37a_idx')],
            },
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['-fixed', '-created_at', 'status'], name='app_article_fixed_c88256_idx'),
        ),
    ]