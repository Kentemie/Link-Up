import os

from uuid import uuid4
from datetime import datetime
from urllib.parse import urljoin

from django.utils.text import slugify
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from PIL import Image, ImageOps


def unique_slugify(instance, slug):
    
    model = instance.__class__
    unique_slug = slugify(slug)

    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = f"{unique_slug}-{uuid4().hex[:8]}"

    return unique_slug


def get_client_ip(request):
    """
    Get user's IP
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
    return ip


def image_compress(image_path, height, width):
    image = Image.open(image_path)

    if image.mode != 'RGB':
        image = image.convert('RGB')
    if image.height > height or image.width > width:
        output_size = (height, width)
        image.thumbnail(output_size)
    
    image = ImageOps.exif_transpose(image)
    image.save(image_path, format='JPEG', quality=90, optimize=True)

    """
    Image.open(image_path) - opens the image specified in the image_path variable using the PIL (Python Imaging Library) library.

    if img.mode != 'RGB': img = img.convert('RGB') - checks that the image is in RGB format. If this is not the case, then the image 
    is converted to RGB.

    if img.height > height or img.width > width: - checks whether the height or width of the image is greater than the specified
    values. If yes, then the image will be proportionally reduced to the height and width dimensions while maintaining the aspect ratio.

    output_size = (height, width) img.thumbnail(output_size) - Reduces the size of the image if it exceeds the specified dimensions,
    while maintaining the aspect ratio.

    img = ImageOps.exif_transpose(img) - Determines the orientation of the image and transforms it according to the EXIF data so 
    that the image is displayed correctly.

    img.save(image_path, format='JPEG', quality=90, optimize=True) - saves the optimized image in the specified image_path in JPEG 
    format with quality 90 and optimization enabled.
    """



class CkeditorCustomStorage(FileSystemStorage):
    """
    Custom location for editor media files
    """
    
    def get_folder_name(self):
        return datetime.now().strftime('%Y/%m/%d')

    def get_valid_name(self, name):
        return name

    def _save(self, name, content):
        folder_name = self.get_folder_name()
        name = os.path.join(folder_name, self.get_valid_name(name))
        return super()._save(name, content)

    location = os.path.join(settings.MEDIA_ROOT, 'uploads/')
    base_url = urljoin(settings.MEDIA_URL, 'uploads/')