from django.db import models
from django.utils import timezone

class ScrapedCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class ScrapedArticle(models.Model):
    title = models.CharField(max_length=255)
    article_link = models.URLField(unique=True)
    content = models.TextField(blank=True, null=True)
    category = models.ForeignKey(ScrapedCategory, on_delete=models.SET_NULL, null=True)
    date_published = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
        


