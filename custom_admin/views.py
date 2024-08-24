from django.shortcuts import render
from django.http import JsonResponse
import threading
from django.core.management import call_command
from scraper.models import ScrapedArticle
from X.models import Article, PublishedArticle

def run_command(command, *args, **kwargs):
    call_command(command, *args, **kwargs)

def task_dashboard(request):
    return render(request, 'custom_admin/task_dashboard.html')

def get_progress(model, filter_dict=None):
    if filter_dict:
        return model.objects.filter(**filter_dict).count()
    return model.objects.count()

def start_task(request, task_name):
    if task_name == 'scrape':
        limit = int(request.GET.get('limit', 20))  # Default limit is 20 if not specified
        threading.Thread(target=run_command, args=('start_scraping',), kwargs={'limit': limit}).start()
        return JsonResponse({
            'status': f'Scrape task started with limit {limit}',
            'limit': limit
        })

    elif task_name == 'rephrase':
        threading.Thread(target=run_command, args=('rephrase_articles',)).start()
        total_articles = ScrapedArticle.objects.count()
        return JsonResponse({
            'status': 'Rephrase task started',
            'total': total_articles
        })

    elif task_name == 'post':
        threading.Thread(target=run_command, args=('post_articles',)).start()
        total_articles = Article.objects.filter(is_published=False).count()
        return JsonResponse({
            'status': 'Post task started',
            'total': total_articles
        })

    return JsonResponse({'status': 'Invalid task name'})

def get_task_progress(request, task_name):
    progress = 0
    total = 0

    if task_name == 'scrape':
        progress = get_progress(ScrapedArticle)
        total = int(request.GET.get('limit', 20))  # Use the limit provided when starting the task
    elif task_name == 'rephrase':
        progress = Article.objects.count()
        total = ScrapedArticle.objects.count()  # Track against the total scraped articles
    elif task_name == 'post':
        progress = PublishedArticle.objects.count()
        total = Article.objects.count()  # Track against all articles (published and unpublished)

    return JsonResponse({
        'progress': progress,
        'total': total
    })
