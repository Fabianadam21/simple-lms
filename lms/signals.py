from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from .models import Course


@receiver(pre_save, sender=Course)
def auto_generate_course_slug(sender, instance, **kwargs):
    """
    Auto-generate slug for Course based on title if not provided
    """
    if not instance.slug:
        instance.slug = slugify(instance.title)
