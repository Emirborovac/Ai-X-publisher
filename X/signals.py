from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Article, PublishedArticle
from django.utils import timezone

@receiver(post_save, sender=Article)
def move_to_published(sender, instance, created, **kwargs):
    if instance.is_published:
        PublishedArticle.objects.create(
            title=instance.title,
            article_link=instance.article_link,
            image_link=instance.image_link,
            rephrased_article=instance.rephrased_article,
            image_path=instance.image_path,
            date_created=instance.date_created,
            category=instance.category,
            date_published=timezone.now()
        )
        instance.delete()
