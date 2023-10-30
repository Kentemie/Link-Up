from django.db import models
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache

from modules.services.utils import unique_slugify


User = get_user_model()



class Profile(models.Model):
    
    class Meta:
        db_table = 'app_profiles'
        ordering = ('user',)
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'


    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile'
    )
    slug = models.SlugField(
        verbose_name='URL', 
        max_length=255, 
        blank=True, 
        unique=True
    )
    following = models.ManyToManyField(
        'self', 
        verbose_name='Subscriptions', 
        related_name='followers', 
        symmetrical=False, 
        blank=True
    )
    avatar = models.ImageField(
        verbose_name='Avatar',
        upload_to='images/avatars/%Y/%m/%d/', 
        default='images/avatars/avatar.jpg',
        blank=True,  
        validators=[
            FileExtensionValidator(allowed_extensions=('png', 'jpg', 'jpeg'))
        ]
    )
    bio = models.TextField(
        max_length=500, 
        blank=True, 
        verbose_name='Personal information'
    )
    birth_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='Date of birth'
    )


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.user.username)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.user.username
    
    def get_absolute_url(self):
        return reverse('system:profile_detail', kwargs={'slug': self.slug})
    
    def is_online(self):
        cache_key = f'last-seen-{self.user.id}'
        last_seen = cache.get(cache_key)
        
        if last_seen is not None and (timezone.now() < last_seen + timezone.timedelta(seconds=300)):
            return True
        return False

    @property
    def get_avatar(self):
        if self.avatar:
            return self.avatar.url
        return f'https://ui-avatars.com/api/?size=150&background=random&name={self.slug}'
    


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()



class Feedback(models.Model):

    class Meta:
        db_table = 'app_feedback'
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback'
        ordering = ['-created_at']


    subject = models.CharField(
        max_length=255, 
        verbose_name='Letter subject'
    )
    email = models.EmailField(
        max_length=255, 
        verbose_name='Email address'
    )
    content = models.TextField(
        verbose_name='Contents of the letter'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Date the letter was sent'
    )
    ip_address = models.GenericIPAddressField(
        verbose_name='Sender IP',  
        blank=True, 
        null=True
    )
    user = models.ForeignKey(
        User, 
        verbose_name='User', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )


    def __str__(self):
        return f'You have a letter from {self.email}'