from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=255)
    article_link = models.URLField(unique=True)
    image_link = models.CharField(max_length=400,blank=True, null=True)
    rephrased_article = models.TextField(blank=True, null=True)
    image_path = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class RawArticle(models.Model):
    title = models.CharField(max_length=255)
    article_link = models.URLField(unique=True)
    date_published = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title

from django.db import models
from django.utils import timezone

class PublishedArticle(models.Model):
    title = models.CharField(max_length=255)
    article_link = models.URLField(unique=False)
    image_link = models.CharField(max_length=400, blank=True, null=True)
    rephrased_article = models.TextField(blank=True, null=True)
    image_path = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    date_published = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Published: {self.title}"

class PostingSchedule(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    is_posted = models.BooleanField(default=False)

    def __str__(self):
        return f"Post '{self.article.title}' at {self.scheduled_time}"


from django.db import models

class WebsiteInput(models.Model):
    url = models.URLField(unique=True)
    selectors = models.TextField()

    def __str__(self):
        return self.url



