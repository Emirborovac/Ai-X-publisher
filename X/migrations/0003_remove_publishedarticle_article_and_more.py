# Generated by Django 5.1 on 2024-08-20 11:32

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('X', '0002_article_is_published_publishedarticle'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publishedarticle',
            name='article',
        ),
        migrations.AddField(
            model_name='publishedarticle',
            name='article_link',
            field=models.URLField(default='https://example.com/default-link', unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='publishedarticle',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='X.category'),
        ),
        migrations.AddField(
            model_name='publishedarticle',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='publishedarticle',
            name='image_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='publishedarticle',
            name='image_path',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='publishedarticle',
            name='rephrased_article',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='publishedarticle',
            name='title',
            field=models.CharField(default='Default Title', max_length=255),
            preserve_default=False,
        ),
    ]