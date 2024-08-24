# Generated by Django 4.2.7 on 2024-08-21 18:04

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('X', '0006_alter_article_image_link'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publishedarticle',
            name='article',
        ),
        migrations.AddField(
            model_name='publishedarticle',
            name='article_link',
            field=models.URLField(default='http://default-link.com', unique=True),
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
            field=models.CharField(blank=True, max_length=400, null=True),
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
            field=models.CharField(default='default', max_length=255),
            preserve_default=False,
        ),
    ]
