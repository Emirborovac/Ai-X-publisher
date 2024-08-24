from django.contrib import admin
from .models import ScrapedCategory, ScrapedArticle

class ScrapedCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

class ScrapedArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'article_link', 'date_published', 'category']

admin.site.register(ScrapedCategory, ScrapedCategoryAdmin)
admin.site.register(ScrapedArticle, ScrapedArticleAdmin)
