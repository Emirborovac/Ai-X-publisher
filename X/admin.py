from django.contrib import admin
from .models import Category, Article, PublishedArticle, PostingSchedule, WebsiteInput

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'article_link', 'date_created', 'category', 'is_published']

class PublishedArticleAdmin(admin.ModelAdmin):
    list_display = ['get_article_title', 'get_article_link', 'date_published']

    def get_article_title(self, obj):
        return obj.title

    def get_article_link(self, obj):
        return obj.article_link

    get_article_title.short_description = 'Article Title'
    get_article_link.short_description = 'Article Link'

class WebsiteInputAdmin(admin.ModelAdmin):
    list_display = ['url', 'selectors']

admin.site.register(Category, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(PublishedArticle, PublishedArticleAdmin)
admin.site.register(PostingSchedule)
admin.site.register(WebsiteInput, WebsiteInputAdmin)
